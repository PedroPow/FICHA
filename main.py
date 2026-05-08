import discord
from discord.ext import commands
from discord import ui
import sqlite3
import re
import os

# ==========================================
# CONFIGURAÇÕES
# ==========================================
TOKEN = os.getenv("TOKEN_ROTA")
FORUM_CHANNEL_ID = 1501020005477912667
DATABASE_NAME = "fichas_policiais.db"
AUTHORIZED_ROLES = [1497235189296791652] 

SITUACOES = ["Efetivo", "Estágio", "Exonerado", "Baixa"]

# ==========================================
# LISTAS
# ==========================================

PATENTES = [
    ("Soldado PM", "<:SD:1480800971604103310>"), ("Cabo PM", "<:CABO:1480800948434767965>"),
    ("Aluno-Sargento PM", "<:AlunoSargento:1495511772256538654>"), ("3º Sargento PM", "<:3SGT:1480800757027573833>"), 
    ("2º Sargento PM", "<:2SGT:1480800372267421850>"), ("1º Sargento PM", "<:1SGT:1480800346375983226>"), 
    ("Subtenente PM", "<:SUBTEN:1480800319553273898>"), ("Aspirante Oficial", "<:ASPOFC:1480800296748847205>"), 
    ("2° Tenente PM", "<:2TENENTE:1480800246337638511>"), ("1° Tenente PM", "<:1TENENTE:1480800221930983538>"), 
    ("Capitão PM", "<:CAPITO:1480800193841463367>"), ("Major PM", "<:MAJOR:1480800161646116956>"), 
    ("Tenente Coronel PM", "<:TENCEL:1480800122341298186>")
]

MEDALHAS = [
    ("CENTENARIO DE ROTA", "<:CENTENARIO_ROTA:1501023340578476165>"), ("CENTENARIO APMBB", "<:CENTENARIO_APMBB:1501023453266841741>"),
    ("CENTENARIO ESSGT", "<:ESSgt:1501023754812260454>"), ("CENTENARIO DSA CG", "<:DSA_CG:1501023707685060730>"),
    ("MERITO DA JUSTIÇA E DISCIPLINA", "<:JUSTICA_DISCIPLINA:1501024033490337872>"), ("MERITO E DEDICAÇÃO", "<:DEDICACAO:1501024134182731806>"),
    ("PEDRO DIAS DE CAMPOS", "<:PEDRO_D_C:1501024183302492180>"), ("SISQUENTENÁRIO DA PM", "<:150_PMESP:1501024260091547648>"),
    ("VALOR MILITAR OURO", "<:VALOR_MILITAR:1501025277688549458>"), ("VALOR MILITAR PRATA", "<:VALOR_MILITAR:1501025277688549458>"),
    ("VALOR MILITAR BRONZE", "<:VALOR_MILITAR:1501025277688549458>"), ("MEDALHA FORÇA TÁTICA", "<:MEDALHA_FT:1501023860731150671>"),
    ("MERITO DAS COMUNICAÇÕES", "<:COMUNICACAO:1501024095893065778>"), ("MEDALHA ROCAM", "<:ROCAM:1501024212364693534>")
]

CURSOS = [
    ("Curso Op. Especial", "<:CURSO1:1500711626221945002>"), ("Curso Superior de Polícia Militar", "<:CURSO1:1500711626221945002>"),
    ("Curso de Aperfeiçoamento de Oficiais", "<:CURSO1:1500711626221945002>"), ("Curso de Formação de Oficiais", "<:CURSO1:1500711626221945002>"),
    ("Curso de Formação de Sargentos", "<:CURSO1:1500711626221945002>"), ("Curso de Formação de Cabos", "<:CURSO1:1500711626221945002>"),
    ("Curso de Formação de Soldados", "<:CURSO1:1500711626221945002>"), ("Curso de P.O.P", "<:CURSO1:1500711626221945002>"),
    ("Curso de Abordagem e Posicionamento", "<:CURSO1:1500711626221945002>"), ("Curso de Modulação", "<:CURSO1:1500711626221945002>"),
    ("Curso de Confecção de BOPM", "<:CURSO1:1500711626221945002>"), ("Curso de TAT I", "<:CURSO1:1500711626221945002>"),
    ("Curso de TAT II", "<:CURSO1:1500711626221945002>"), ("Curso de TAT III", "<:CURSO1:1500711626221945002>"),
    ("SAT A", "<:CURSO1:1500711626221945002>"), ("SAT B", "<:CURSO1:1500711626221945002>")
]

LAUREAS = [
    ("LÁUREA 5° Grau", "<:lurea5:1481619463840333845>"), ("LÁUREA 4° Grau", "<:lurea4:1481619742757224478>"),
    ("LÁUREA 3° Grau", "<:lurea3:1481619849133424690>"), ("LÁUREA 2° Grau", "<:lurea2:1481619935745806426>"),
    ("LÁUREA 1° Grau", "<:lurea1:1481620008650932347>")
]

# ==========================================
# UTILITÁRIOS
# ==========================================

def parse_emoji(emoji_str):
    if not emoji_str: return None
    match = re.match(r"<:([a-zA-Z0-9_]+):(\d+)>", emoji_str)
    if match:
        name, id_ = match.groups()
        return discord.PartialEmoji(name=name, id=int(id_))
    return emoji_str

# ==========================================
# BANCO DE DADOS
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
            cursos TEXT DEFAULT '', certificados TEXT DEFAULT '',
            thread_id TEXT DEFAULT ''
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
            txt_med += f"{m_emoji} {m_name}\n"
    embed.add_field(name="MEDALHAS:", value=f"{txt_med if txt_med else 'Nenhuma'}\n------------------------------", inline=False)

    txt_cur = ""
    if f['cursos']:
        for c_name in f['cursos'].split(", "):
            c_emoji = next((e for n, e in CURSOS if n == c_name), "📚")
            txt_cur += f"{c_emoji} {c_name}\n"
    embed.add_field(name="CURSOS:", value=f"{txt_cur if txt_cur else 'Nenhum'}\n------------------------------", inline=False)

    txt_cert = ""
    if f['certificados']:
        for cert in f['certificados'].split(", "):
            txt_cert += f"🎓 {cert}\n"
    embed.add_field(name="CERTIFICADOS:", value=f"{txt_cert if txt_cert else 'Nenhum'}\n------------------------------", inline=False)

    return embed

# ==========================================
# SELECTS E MODAIS
# ==========================================

class ModalCertificado(ui.Modal, title="Gerenciar Certificados"):
    numero = ui.TextInput(label="N° do CERTIFICADO", placeholder="Ex: ROTA-2026-0001", required=True, max_length=50)

    async def on_submit(self, interaction: discord.Interaction):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM fichas WHERE thread_id = ?", (str(interaction.channel_id),))
        f = cursor.fetchone()
        conn.close()

        if not f:
            return await interaction.response.send_message("❌ Ficha não encontrada.", ephemeral=True)

        user_id = f['user_id']
        certificados = f['certificados'].split(", ") if f['certificados'] else []
        numero = self.numero.value.strip()

        if numero in certificados:
            certificados.remove(numero)
            msg = f"❌ Certificado removido: `{numero}`"
        else:
            certificados.append(numero)
            msg = f"✅ Certificado adicionado: `{numero}`"

        final = ", ".join([c for c in certificados if c])
        update_ficha(user_id, certificados=final)

        # Atualiza mensagem da thread
        async for message in interaction.channel.history(limit=20):
            if message.author == interaction.client.user and message.embeds and message.embeds[0].title == "📁 PRONTUÁRIO POLICIAL":
                await message.edit(embed=gerar_embed_ficha(user_id))
                break

        await interaction.response.send_message(msg, ephemeral=True)

class MenuPrincipal(ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Gerenciar Patente", emoji="🎖️", value="patente"),
            discord.SelectOption(label="Gerenciar Situação", emoji="📋", value="situacao"),
            discord.SelectOption(label="Gerenciar Láurea", emoji="🏅", value="laurea"),
            discord.SelectOption(label="Gerenciar Cursos", emoji="📚", value="cursos"),
            discord.SelectOption(label="Gerenciar Medalhas", emoji="🎗️", value="medalhas"),
            discord.SelectOption(label="Gerenciar Certificados", emoji="🎓", value="certificados")
        ]
        super().__init__(placeholder="Selecione uma opção...", options=options, custom_id="menu_principal")

    async def callback(self, interaction: discord.Interaction):
        valor = self.values[0]
        if valor == "patente": await interaction.response.send_message(view=ViewPatente(), ephemeral=True)
        elif valor == "situacao": await interaction.response.send_message(view=ViewSituacao(), ephemeral=True)
        elif valor == "laurea": await interaction.response.send_message(view=ViewLaurea(), ephemeral=True)
        elif valor == "cursos": await interaction.response.send_message(view=ViewCursos(), ephemeral=True)
        elif valor == "medalhas": await interaction.response.send_message(view=ViewMedalhas(), ephemeral=True)
        elif valor == "certificados": await interaction.response.send_modal(ModalCertificado())

# Views de Suporte
class ViewPatente(ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        self.add_item(SelectGeral(PATENTES, "Selecionar patente", "patente", "s_p"))

class ViewSituacao(ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        self.add_item(SelectGeral([(s, None) for s in SITUACOES], "Selecionar situação", "situacao", "s_s"))

class ViewLaurea(ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        self.add_item(SelectGeral(LAUREAS, "Selecionar láurea", "laurea", "s_l"))

class ViewCursos(ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        self.add_item(SelectGeral(CURSOS, "Gerenciar cursos", "cursos", "s_c", True))

class ViewMedalhas(ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        self.add_item(SelectGeral(MEDALHAS, "Gerenciar medalhas", "medalhas", "s_m", True))

class SelectGeral(ui.Select):
    def __init__(self, options_data, placeholder, db_field, custom_id, multi=False):
        self.db_field = db_field
        self.multi = multi
        processed_options = []
        for label, emoji_str in options_data:
            emoji_obj = parse_emoji(emoji_str)
            processed_options.append(discord.SelectOption(label=label, emoji=emoji_obj if isinstance(emoji_obj, discord.PartialEmoji) else None))

        super().__init__(placeholder=placeholder, min_values=1, max_values=1, options=processed_options, custom_id=custom_id)

    async def callback(self, interaction: discord.Interaction):
        if not any(role.id in AUTHORIZED_ROLES for role in interaction.user.roles):
            return await interaction.response.send_message("❌ Sem permissão.", ephemeral=True)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM fichas WHERE thread_id = ?", (str(interaction.channel_id),))
        f = cursor.fetchone()
        conn.close()

        if not f: return await interaction.response.send_message("❌ Ficha não encontrada.", ephemeral=True)

        selecionado = self.values[0]
        if self.multi:
            itens = f[self.db_field].split(", ") if f[self.db_field] else []
            if selecionado in itens: itens.remove(selecionado)
            else: itens.append(selecionado)
            final = ", ".join([x for x in itens if x and x not in ["Nenhuma", "Nenhum"]])
        else:
            final = selecionado

        update_ficha(f['user_id'], **{self.db_field: final})
        
        # Atualiza mensagem da thread
        async for message in interaction.channel.history(limit=20):
            if message.author == interaction.client.user and message.embeds and message.embeds[0].title == "📁 PRONTUÁRIO POLICIAL":
                await message.edit(embed=gerar_embed_ficha(f['user_id']))
                break

        await interaction.response.send_message(f"✅ Atualizado: {selecionado}", ephemeral=True)

class EdicaoFichaView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(MenuPrincipal())

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

# ==========================================
# BOT E INICIALIZAÇÃO
# ==========================================

class BotPolicial(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())

    async def setup_hook(self):

        init_db()

        self.add_view(EdicaoFichaView())

        view_registro = ui.View(timeout=None)

        btn = ui.Button(
            label="Criar Prontuário",
            style=discord.ButtonStyle.secondary,
            emoji="📁",
            custom_id="reg_prontuario"
        )

        async def btn_callback(interaction):
            await interaction.response.send_modal(
                ModalCriarFicha()
            )

        btn.callback = btn_callback

        view_registro.add_item(btn)

        self.add_view(view_registro)

    async def on_ready(self):
        print(f"✅ Bot online como {self.user}")
        await self.verificar_painel_automatico()

    async def verificar_painel_automatico(self):
        ID_CANAL_REGISTRO = 1501019443013095524 
        canal = self.get_channel(ID_CANAL_REGISTRO)
        if not canal: return

        embed = discord.Embed(
            title="📁 Emitir Prontuário",
            description=f"> **Painel de emissão de prontuário policial.**\n> Policiais responsáveis: <@&{AUTHORIZED_ROLES[0]}>\n\n> **Clique no botão abaixo para criar seu prontuário.**",
            color=16711424
        )
        embed.set_image(url="https://www.cidadaonet.com.br/storage/conteudo/large/398092680684acacc4a357.jpg")
        
        view = ui.View(timeout=None)
        btn = ui.Button(label="Criar Prontuário", style=discord.ButtonStyle.secondary, emoji="📁", custom_id="reg_prontuario")
        async def btn_callback(interaction): await interaction.response.send_modal(ModalCriarFicha())
        btn.callback = btn_callback
        view.add_item(btn)

        async for message in canal.history(limit=10):
            if message.author == self.user and message.embeds and message.embeds[0].title == "📁 Emitir Prontuário":
                await message.edit(embed=embed, view=view)
                return
        await canal.send(embed=embed, view=view)

bot = BotPolicial()
bot.run(TOKEN)