import discord
from discord.ext import commands
from discord import ui
import sqlite3
import re
import os

# ==========================================
# CONFIGURAÇÕES
# ==========================================
TOKEN = os.getenv("TOKEN_ROTA")  # Certifique-se de definir a variável de ambiente com seu token
FORUM_CHANNEL_ID = 1501020005477912667
DATABASE_NAME = "fichas_policiais.db"
AUTHORIZED_ROLES = [1497235189296791652] # IDs dos cargos autorizados a usar os comandos (ex: P1 - Recurso Humano) 

SITUACOES = ["Efetivo", "Estágio", "Exonerado", "Baixa"]

# ==========================================
# LISTAS CORRIGIDAS (APENAS NOME:ID)
# ==========================================

PATENTES = [
    ("Soldado PM", "<:SD:1480800971604103310>"), 
    ("Cabo PM", "<:CABO:1480800948434767965>"),
    ("Aluno-Sargento PM", "<:AlunoSargento:1495511772256538654>"),
    ("3º Sargento PM", "<:3SGT:1480800757027573833>"), 
    ("2º Sargento PM", "<:2SGT:1480800372267421850>"),
    ("1º Sargento PM", "<:1SGT:1480800346375983226>"), 
    ("Subtenente PM", "<:SUBTEN:1480800319553273898>"),
    ("Aspirante Oficial", "<:ASPOFC:1480800296748847205>"), 
    ("2° Tenente PM", "<:2TENENTE:1480800246337638511>"),
    ("1° Tenente PM", "<:1TENENTE:1480800221930983538>"), 
    ("Capitão PM", "<:CAPITO:1480800193841463367>"),
    ("Major PM", "<:MAJOR:1480800161646116956>"), 
    ("Tenente Coronel PM", "<:TENCEL:1480800122341298186>")
]

MEDALHAS = [
    ("CENTENARIO DE ROTA", "<:CENTENARIO_ROTA:1501023340578476165>"),
    ("CENTENARIO APMBB", "<:CENTENARIO_APMBB:1501023453266841741>"),
    ("CENTENARIO ESSGT", "<:ESSgt:1501023754812260454>"),
    ("CENTENARIO DSA CG", "<:DSA_CG:1501023707685060730>"),
    ("MERITO DA JUSTIÇA E DISCIPLINA", "<:JUSTICA_DISCIPLINA:1501024033490337872>"),
    ("MERITO E DEDICAÇÃO", "<:DEDICACAO:1501024134182731806>"),
    ("PEDRO DIAS DE CAMPOS", "<:PEDRO_D_C:1501024183302492180>"),
    ("SISQUENTENÁRIO DA PM", "<:150_PMESP:1501024260091547648>"),
    ("VALOR MILITAR OURO", "<:VALOR_MILITAR:1501025277688549458>"),
    ("VALOR MILITAR PRATA", "<:VALOR_MILITAR:1501025277688549458>"),
    ("VALOR MILITAR BRONZE", "<:VALOR_MILITAR:1501025277688549458>"),
    ("MEDALHA FORÇA TÁTICA", "<:MEDALHA_FT:1501023860731150671>"),
    ("MERITO DAS COMUNICAÇÕES", "<:COMUNICACAO:1501024095893065778>"),
    ("MEDALHA ROCAM", "<:ROCAM:1501024212364693534>")  
]

CURSOS = [
    ("Curso Op. Especial", "<:CURSO1:1500711626221945002>"),
    ("Curso Superior de Polícia Militar", "<:CURSO1:1500711626221945002>"),
    ("Curso de Aperfeiçoamento de Oficiais", "<:CURSO1:1500711626221945002>"),
    ("Curso de Formação de Oficiais", "<:CURSO1:1500711626221945002>"),
    ("Curso de Formação de Sargentos", "<:CURSO1:1500711626221945002>"),
    ("Curso de Formação de Cabos", "<:CURSO1:1500711626221945002>"),
    ("Curso de Formação de Soldados", "<:CURSO1:1500711626221945002>"),
    ("Curso de P.O.P", "<:CURSO1:1500711626221945002>"),
    ("Curso de Abordagem e Posicionamento", "<:CURSO1:1500711626221945002>"),
    ("Curso de Modulação", "<:CURSO1:1500711626221945002>"),
    ("Curso de Confecção de BOPM", "<:CURSO1:1500711626221945002>"),
    ("Curso de TAT I", "<:CURSO1:1500711626221945002>"),
    ("Curso de TAT II", "<:CURSO1:1500711626221945002>"),
    ("Curso de TAT III", "<:CURSO1:1500711626221945002>"),
    ("SAT A", "<:CURSO1:1500711626221945002>"),
    ("SAT B", "<:CURSO1:1500711626221945002>"),

]

LAUREAS = [
    ("LÁUREA 5° Grau", "<:lurea5:1481619463840333845>"),
    ("LÁUREA 4° Grau", "<:lurea4:1481619742757224478>"),
    ("LÁUREA 3° Grau", "<:lurea3:1481619849133424690>"),
    ("LÁUREA 2° Grau", "<:lurea2:1481619935745806426>"),
    ("LÁUREA 1° Grau", "<:lurea1:1481620008650932347>")
]

# ==========================================
# BANCO DE DADOS E LÓGICA (Mantido do seu original)
# ==========================================
def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fichas (
            user_id TEXT PRIMARY KEY,
            nome TEXT, registro TEXT, foto TEXT DEFAULT '',
            patente TEXT DEFAULT 'Soldado PM', situacao TEXT DEFAULT 'Estágio',
            laurea TEXT DEFAULT 'Nenhuma', medalhas TEXT DEFAULT '',
            cursos TEXT DEFAULT '', thread_id TEXT DEFAULT ''
        )
    ''')
    conn.commit()
    conn.close()

def update_ficha(user_id, **kwargs):
    conn = get_db_connection()
    cursor = conn.cursor()
    for key, value in kwargs.items():
        cursor.execute(f"UPDATE fichas SET {key} = ? WHERE user_id = ?", (str(value), str(user_id)))
    conn.commit()
    conn.close()

def gerar_embed_ficha(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM fichas WHERE user_id = ?", (str(user_id),))
    f = cursor.fetchone()
    conn.close()
    if not f: return None

    embed = discord.Embed(
        title="📁 PRONTUÁRIO POLICIAL", 
        description=f"Nome: `{f['nome']}`\n Registro: `{f['registro']}`\n Situação: `{f['situacao']}`\n\n------------------------------",
        color=0xFFFF00
    )
    if f['foto'] and f['foto'].startswith('http'): embed.set_thumbnail(url=f['foto'])
    
    p_emoji = next((e for p, e in PATENTES if p == f['patente']), "🎖️")
    embed.add_field(name="PATENTE:", value=f"{p_emoji} `{f['patente']}`\n\n------------------------------", inline=False)

    l_emoji = next((e for l, e in LAUREAS if l == f['laurea']), "🏅")
    embed.add_field(name="LÁUREA:", value=f"{l_emoji} `{f['laurea']}`\n\n------------------------------", inline=False)

    txt_med = ""
    if f['medalhas']:
        for m_name in f['medalhas'].split(", "):
            m_emoji = next((e for n, e in MEDALHAS if n == m_name), "🎖️")
            txt_med += f"{m_emoji} {m_name}\n" # Removido crases daqui também
    # CORREÇÃO: Removido as crases de fora da variável txt_med
    embed.add_field(name="MEDALHAS:", value=f"{txt_med if txt_med else 'Nenhuma'}\n------------------------------", inline=False)

    txt_cur = ""
    if f['cursos']:
        for c_name in f['cursos'].split(", "):
            c_emoji = next((e for n, e in CURSOS if n == c_name), "📚")
            txt_cur += f"{c_emoji} {c_name}\n" # Removido crases daqui também
    # CORREÇÃO: Removido as crases de fora da variável txt_cur
    embed.add_field(name="CURSOS:", value=f"{txt_cur if txt_cur else 'Nenhum'}\n------------------------------", inline=False)

    return embed
    
    # padrão <:nome:id>
    match = re.match(r"<:([a-zA-Z0-9_]+):(\d+)>", emoji_str)
    if match:
        name, id_ = match.groups()
        return discord.PartialEmoji(name=name, id=int(id_))
    
    # padrão NOME:ID (tipo suas PATENTES e CURSOS)
    if ":" in emoji_str:
        try:
            name, id_ = emoji_str.split(":")
            return discord.PartialEmoji(name=name, id=int(id_))
        except:
            pass

    # fallback → emoji unicode ou string
    return emoji_str

# ==========================================
# SELECTS E MODAIS
# ==========================================
class SelectGeral(ui.Select):
    def __init__(self, options_data, placeholder, db_field, custom_id, multi=False):
        self.options_data = options_data
        self.db_field = db_field
        self.multi = multi
        
        processed_options = []
        for label, emoji_str in options_data:
            try:
                emoji_obj = parse_emoji(emoji_str)
                processed_options.append(discord.SelectOption(label=label, emoji=emoji_obj))
            except:
                processed_options.append(discord.SelectOption(label=label))

        super().__init__(
            placeholder=placeholder,
            min_values=1,
            max_values=1, # Seleciona um por vez para alternar (Toggle)
            options=processed_options,
            custom_id=custom_id
        )

    async def callback(self, interaction: discord.Interaction):
        # 🔒 Permissão
        if not any(role.id in AUTHORIZED_ROLES for role in interaction.user.roles):
            return await interaction.response.send_message("❌ Sem permissão.", ephemeral=True)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM fichas WHERE thread_id = ?", (str(interaction.channel_id),))
        f = cursor.fetchone()
        conn.close()

        if not f:
            return await interaction.response.send_message("❌ Ficha não encontrada.", ephemeral=True)

        selecionado = self.values[0]
        user_id = f['user_id']
        
        # --- LÓGICA DE TOGGLE (ADICIONAR/REMOVER) ---
        if self.multi:
            # Pega a lista atual do banco
            itens_atuais = f[self.db_field].split(", ") if f[self.db_field] else []
            
            if selecionado in itens_atuais:
                # Se já tem, REMOVE
                itens_atuais.remove(selecionado)
                mensagem_feedback = f"✅ Removido: **{selecionado}**"
            else:
                # Se não tem, ADICIONA
                itens_atuais.append(selecionado)
                mensagem_feedback = f"✅ Adicionado: **{selecionado}**"
            
            # Limpa lixo e reconstrói a string
            itens_atuais = [x for x in itens_atuais if x and x not in ["Nenhuma", "Nenhum"]]
            final_value = ", ".join(itens_atuais)
        else:
            # Para Patente/Situação apenas troca (não remove, pois o policial sempre tem uma)
            final_value = selecionado
            mensagem_feedback = f"✅ Alterado para: **{selecionado}**"

        # 💾 Salva no banco
        update_ficha(user_id, **{self.db_field: final_value})

        # 🔄 Atualiza o Embed e envia uma resposta rápida (ephemeral)
        await interaction.response.edit_message(embed=gerar_embed_ficha(user_id))
        
        # Opcional: Enviar um aviso temporário de que foi alterado
        await interaction.followup.send(mensagem_feedback, ephemeral=True)

class EdicaoFichaView(ui.View):
    def __init__(self, user_id=None):
        super().__init__(timeout=None)
        # Se passarmos o user_id, podemos carregar a ficha e já remover o que ele tem
        valores = self.obter_valores_atuais(user_id) if user_id else {}

        self.add_item(SelectGeral(PATENTES, "Gerenciar Patente", "patente", "s_p"))
        self.add_item(SelectGeral([(s, None) for s in SITUACOES], "Gerenciar Situação", "situacao", "s_s"))
        self.add_item(SelectGeral(LAUREAS, "Gerenciar Láurea", "laurea", "s_l"))
        
        # Selects que usam o filtro
        self.add_item(SelectGeral(CURSOS, "Gerenciar Cursos", "cursos", "s_c", True))
        self.add_item(SelectGeral(MEDALHAS, "Gerenciar Medalhas", "medalhas", "s_m", True))

    def obter_valores_atuais(self, user_id):
        # Opcional: Lógica para carregar do banco no init se desejar
        # que o menu já nasça filtrado ao abrir a thread.
        return {}

class ModalCriarFicha(ui.Modal, title="🚨 Registro de Novo Policial"):
    nome = ui.TextInput(label="Nome no RP", placeholder="Ex: Sargento Oliveira", min_length=3, max_length=50)
    registro = ui.TextInput(label="ID/Registro", placeholder="Ex: 5050", min_length=1, max_length=10)
    foto = ui.TextInput(label="URL da Foto", required=False, placeholder="Link da imagem")

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO fichas (user_id, nome, registro, foto) VALUES (?, ?, ?, ?)", 
                       (str(interaction.user.id), self.nome.value, self.registro.value, self.foto.value))
        conn.commit()
        conn.close()

        forum = interaction.guild.get_channel(FORUM_CHANNEL_ID)
        if isinstance(forum, discord.ForumChannel):
            embed = gerar_embed_ficha(interaction.user.id)
            thread_bundle = await forum.create_thread(name=f"Ficha: {self.nome.value}", embed=embed, view=EdicaoFichaView())
            update_ficha(interaction.user.id, thread_id=str(thread_bundle.thread.id))
            await interaction.followup.send(f"✅ Ficha enviada ao fórum: {thread_bundle.thread.mention}", ephemeral=True)

class BotPolicial(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())

    async def setup_hook(self):
        init_db()
        # 1. Torna os selects das fichas persistentes
        self.add_view(EdicaoFichaView())
        
        # 2. Torna o botão de "Criar Prontuário" persistente (fundamental)
        view_registro = ui.View(timeout=None)
        btn = ui.Button(label="Criar Prontuário", style=discord.ButtonStyle.secondary, emoji="📁", custom_id="reg_prontuario")
        
        async def btn_callback(interaction):
            await interaction.response.send_modal(ModalCriarFicha())
        
        btn.callback = btn_callback
        view_registro.add_item(btn)
        self.add_view(view_registro)

    async def on_ready(self):
        print(f"✅ Bot online como {self.user}")
        await self.verificar_painel_automatico()

    async def verificar_painel_automatico(self):
        # ID do canal onde o botão de registro deve ficar
        ID_CANAL_REGISTRO = 1501019443013095524  # <--- COLOQUE O ID DO CANAL AQUI
        
        canal = self.get_channel(ID_CANAL_REGISTRO)
        if not canal:
            print("❌ Canal de registro não encontrado para o auto-setup.")
            return

        # Configuração do Embed (mesmo do seu comando setup)
        embed = discord.Embed(
            title="📁 Emitir Prontuário",
            description=(
                "> **Painel de emissão de prontuário policial.**\n"
                "> Os prontuários são individuais e intransferíveis.\n"
                "> Somente responsáveis poderão emitir ou editar os prontuários.\n\n"
                f"> Policiais responsáveis: <@&{AUTHORIZED_ROLES[0]}>\n\n"
                "> **Clique no botão abaixo para criar seu prontuário.**"
            ),
            color=16711424
        )
        embed.set_image(url="https://www.cidadaonet.com.br/storage/conteudo/large/398092680684acacc4a357.jpg")
        embed.set_footer(text="Batalhão FT Virtual® Todos direitos reservados.")

        view = ui.View(timeout=None)
        btn = ui.Button(label="Criar Prontuário", style=discord.ButtonStyle.secondary, emoji="📁", custom_id="reg_prontuario")
        
        async def btn_callback(interaction):
            await interaction.response.send_modal(ModalCriarFicha())
        
        btn.callback = btn_callback
        view.add_item(btn)

        # Procura se já existe a mensagem
        mensagem_existente = None
        async for message in canal.history(limit=10):
            if message.author == self.user and message.embeds:
                if message.embeds[0].title == "📁 Emitir Prontuário":
                    mensagem_existente = message
                    break

        if mensagem_existente:
            # Apenas atualiza a mensagem antiga se houver mudanças no código
            await mensagem_existente.edit(embed=embed, view=view)
            print("🔄 Painel de registro atualizado automaticamente.")
        else:
            # Se alguém apagou a mensagem, o bot manda de novo
            await canal.send(embed=embed, view=view)
            print("✨ Novo painel de registro enviado (não foi encontrado anterior).")

bot = BotPolicial()

bot.run(TOKEN)