import discord
from discord.ext import commands
from discord import app_commands
from discord import FFmpegPCMAudio
import json
import random
import os
import asyncio
import functools
import typing


class AClient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.synced = True

    async def on_ready(self):
        print(f'Bot conectado como {self.user.name}')
        print(f'Servidores: {len(self.guilds)}')

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

client = AClient()
tree = app_commands.CommandTree(client)
# DEFINIR PARTE PARA ADMS E PARTE PARA MEMBROS
@tree.command(name="ajuda", description="Lista de Comandos")
async def ajuda(interaction):
    embed = discord.Embed(title="Ajuda - Lista de Comandos", description="Aqui estão os comandos disponíveis:")
    embed.add_field(name="/pic [nome]", value="exp: Ruka, Waifu", inline=False)
    embed.add_field(name="/clear [quantidade]", value="Apaga mensagens do canal. Quantidade máxima: 10.", inline=False)
    embed.add_field(name="/userclear [quantidade]", value="Apaga suas próprias mensagens. Quantidade máxima: 10.", inline=False)
    embed.add_field(name="/excluiruser [user] [motivo] [canal para anunciar a exclusão]", value="Excluir usuário do servidor", inline=False)
    embed.add_field(name="/baniruser [user] [motivo] [canal para anunciar o banimento]", value="Banir usuário do servidor", inline=False)
    embed.add_field(name="/adicionarcargo [para: para quem?] [cargo: cargo novo a ser adicionado]", value="Adicionar cargo a um novo usuário [adicionar cargo para pessoas de outros cargos em manutenção]", inline=False)
    embed.add_field(name="/join", value="Entra no canal de voz.", inline=False)
    embed.add_field(name="/play [link_musica]", value="Reproduz uma música no canal de voz. [Em manutenção]", inline=False)
    embed.add_field(name="/leave", value="Sai do canal de voz.", inline=False)
    embed.add_field(name="/register_server", value="Registra o ID do servidor", inline=False)
    embed.add_field(name="/serverdatasave [chave] [objeto]", value="Adiciona um dado ao registro do servidor", inline=False)
    embed.add_field(name="/server_data [chave]", value="Obtém um dado aleatório para a chave informada", inline=False)
    embed.add_field(name="/showdata", value="Mostra todos os valores do servidor", inline=False)
    embed.add_field(name="/removeobject [chave] [objeto]", value="Remove um objeto do servidor", inline=False)
    embed.add_field(name="/showkeys", value="Mostra todas as chaves registradas do servidor", inline=False)
    embed.add_field(name="/remove_key [chave]", value="Remove uma chave inteira do registro do servidor", inline=False)
    await interaction.response.send_message(embed=embed)

#INICIO SERVER ID JSON -----------------------------

@tree.command(name="register_server", description="Registra o ID do servidor")
@commands.has_permissions(administrator=True)
async def register_server(interaction):
    server_id = str(interaction.guild.id)
    folder_name = "servers_id"
    filename = f"{folder_name}/{server_id}.json"

    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    if os.path.exists(filename):
        await interaction.response.send_message("O servidor já está registrado.")
    else:
        with open(filename, "w") as file:
            json.dump({}, file)

        await interaction.response.send_message(f"Servidor registrado com sucesso. ID: {server_id}")


@tree.command(name="serverdatasave", description="Adiciona um dado ao registro")
@commands.has_permissions(administrator=True)
async def server_data_save(interaction, chave: str, objeto: str):
    server_id = str(interaction.guild.id)
    folder_name = "servers_id"
    filename = f"{folder_name}/{server_id}.json"

    if not os.path.exists(folder_name):
        await interaction.response.send_message("O servidor não está registrado. Por favor, use o comando /register_server para registrar o servidor.")
        return

    if not os.path.exists(filename):
        await interaction.response.send_message("O servidor não possui um registro correspondente. Por favor, verifique se o registro foi feito corretamente.")
        return

    with open(filename, "r") as file:
        data = json.load(file)

    if chave in data:
        data[chave].append(objeto)
    else:
        data[chave] = [objeto]

    with open(filename, "w") as file:
        json.dump(data, file)

    await interaction.response.send_message("Dado adicionado com sucesso.")


@tree.command(name="server_data", description="Obtém um dado aleatório para a chave informada")
async def server_data(interaction, chave: str):
    server_id = str(interaction.guild.id)
    folder_name = "servers_id"
    filename = f"{folder_name}/{server_id}.json"

    if not os.path.exists(folder_name):
        await interaction.response.send_message("O servidor não possui dados registrados.")
        return

    if not os.path.exists(filename):
        await interaction.response.send_message("O servidor não possui um registro correspondente. Por favor, verifique se o registro foi feito corretamente.")
        return

    with open(filename, "r") as file:
        data = json.load(file)

    if chave in data:
        values = data[chave]
        if values:
            random_value = random.choice(values)
            await interaction.response.send_message(f"{random_value}")
        else:
            await interaction.response.send_message(f"A chave '{chave}' não possui valores registrados.")
    else:
        await interaction.response.send_message(f"A chave '{chave}' não foi encontrada.")


@tree.command(name="showdata", description="Mostra todos os valores do servidor")
@commands.has_permissions(administrator=True)
async def show_data(interaction):
    server_id = str(interaction.guild.id)
    folder_name = "servers_id"
    filename = f"{folder_name}/{server_id}.json"

    if not os.path.exists(folder_name):
        await interaction.response.send_message("O servidor não possui dados registrados.")
        return

    if not os.path.exists(filename):
        await interaction.response.send_message("O servidor não possui um registro correspondente. Por favor, verifique se o registro foi feito corretamente.")
        return

    with open(filename, "r") as file:
        data = json.load(file)

    if data:
        response = "\n".join([f"Chave: {key}\nValores: {', '.join(values)}\n" for key, values in data.items()])
        await interaction.response.send_message(response)
    else:
        await interaction.response.send_message("O servidor não possui dados registrados.")


@tree.command(name="removeobject", description="Remove um objeto do servidor")
@commands.has_permissions(administrator=True)
async def remove_object(interaction, chave: str, objeto: str):
    server_id = str(interaction.guild.id)
    folder_name = "servers_id"
    filename = f"{folder_name}/{server_id}.json"

    if not os.path.exists(folder_name):
        await interaction.response.send_message("O servidor não possui dados registrados.")
        return

    if not os.path.exists(filename):
        await interaction.response.send_message("O servidor não possui um registro correspondente. Por favor, verifique se o registro foi feito corretamente.")
        return

    with open(filename, "r") as file:
        data = json.load(file)

    if chave in data and objeto in data[chave]:
        data[chave].remove(objeto)

        with open(filename, "w") as file:
            json.dump(data, file)

        await interaction.response.send_message(f"Objeto '{objeto}' removido com sucesso.")
    else:
        await interaction.response.send_message("A chave ou objeto não foram encontrados.")


@tree.command(name="showkeys", description="Mostra todas as chaves registradas do servidor")
@commands.has_permissions(administrator=True)
async def show_keys(interaction):
    server_id = str(interaction.guild.id)
    folder_name = "servers_id"
    filename = f"{folder_name}/{server_id}.json"

    if not os.path.exists(folder_name):
        await interaction.response.send_message("O servidor não possui dados registrados.")
        return

    if not os.path.exists(filename):
        await interaction.response.send_message("O servidor não possui um registro correspondente. Por favor, verifique se o registro foi feito corretamente.")
        return

    with open(filename, "r") as file:
        data = json.load(file)

    if data:
        key_list = "\n".join(data.keys())

        embed = discord.Embed(
            title="Chaves Registradas",
            description=f"Lista de chaves registradas para o servidor {interaction.guild.name}",
            color=discord.Color.yellow()
        )
        embed.add_field(name="Chaves:", value=key_list, inline=False)

        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("O servidor não possui dados registrados.")


@tree.command(name="remove_key", description="Remove uma chave inteira do registro do servidor")
@commands.has_permissions(administrator=True)
async def remove_key(interaction, chave: str):
    server_id = str(interaction.guild.id)
    folder_name = "servers_id"
    filename = f"{folder_name}/{server_id}.json"

    if not os.path.exists(folder_name):
        await interaction.response.send_message("O servidor não possui dados registrados.")
        return

    if not os.path.exists(filename):
        await interaction.response.send_message("O servidor não possui um registro correspondente. Por favor, verifique se o registro foi feito corretamente.")
        return

    with open(filename, "r") as file:
        data = json.load(file)

    if chave in data:
        del data[chave]

        with open(filename, "w") as file:
            json.dump(data, file)

        await interaction.response.send_message(f"A chave '{chave}' foi removida do registro do servidor.")
    else:
        await interaction.response.send_message(f"A chave '{chave}' não foi encontrada no registro do servidor.")

#FIM JSON SERVER ID



@tree.command(name="adicionarcargo", description="Adiciona um cargo novo para usuário marcado")
@commands.has_permissions(administrator=True)
async def adicionarcargo(interaction, para: typing.Union[discord.Role, discord.Member], cargo: discord.Role):
    # Verifica se o usuário que executou o comando é um administrador
    if not interaction.user.guild_permissions.administrator:
        response = "Você não tem permissão para executar este comando."
        await interaction.response.send_message(response, ephemeral=True)
        return

    members = []

    if isinstance(para, discord.Role):
        members = [member for member in interaction.guild.members if para.id in [role.id for role in member.roles]]
    elif isinstance(para, discord.Member):
        members = [para]

    

    for member in members:
        try:
            await member.add_roles(cargo)
        except discord.Forbidden:
            response = "Desculpe, não tenho permissão para adicionar o cargo aos membros."
            await interaction.response.send_message(response, ephemeral=True)
            return

    if not cargo.hoist:
        response = "Não é possível adicionar o cargo selecionado, pois ele está configurado para não ser mostrado separadamente na lista de cargos."
        await interaction.response.send_message(response, ephemeral=True)
        return

    response = f"{para.mention} recebeu o novo cargo {cargo.mention}."
    await interaction.response.send_message(response, ephemeral=False)



















@tree.command(name="baniruser", description="Bane um usuário do servidor")
@commands.has_permissions(administrator=True)
async def baniruser(interaction, nome: str, motivo: str, canal: discord.TextChannel):
    # Verifica se o usuário que executou o comando é um administrador
    if not interaction.user.guild_permissions.administrator:
        response = "Você não tem permissão para executar este comando."
        await interaction.response.send_message(response, ephemeral=True)
        return

    # Verifica se há usuários mencionados na interação
    if interaction.data.get("resolved").get("users"):
        member_id = next(iter(interaction.data.get("resolved").get("users")))
        member = await interaction.guild.fetch_member(member_id)
        
        try:
            await interaction.guild.ban(member, reason=motivo)
            embed = discord.Embed(title="Banimento", description=f"Usuário banido: {member.mention}\nMotivo: {motivo}")
            embed.set_image(url=member.avatar.url)
            await canal.send(embed=embed)
        except discord.Forbidden:
            response = f"Não foi possível banir o usuário {member.mention}. Não tenho permissão suficiente."
            await interaction.response.send_message(response, ephemeral=True)
            return

    else:
        response = "Nenhum usuário foi mencionado."
        await interaction.response.send_message(response, ephemeral=True)
        return

    response = f"O usuário {member.mention} foi banido do servidor. Motivo: {motivo}"
    await interaction.response.send_message(response, ephemeral=True)








@tree.command(name="excluiruser", description="Exclui um usuário do servidor")
@commands.has_permissions(administrator=True)
async def excluiruser(interaction, nome: str, motivo: str, canal: discord.TextChannel):
    # Verifica se o usuário que executou o comando é um administrador
    if not interaction.user.guild_permissions.administrator:
        response = "Você não tem permissão para executar este comando."
        await interaction.response.send_message(response, ephemeral=True)
        return

    # Verifica se há usuários mencionados na interação
    if interaction.data.get("resolved").get("users"):
        member_id = next(iter(interaction.data.get("resolved").get("users")))

        try:
            member = await interaction.guild.fetch_member(member_id)
        except discord.NotFound:
            response = "Usuário não encontrado no servidor."
            await interaction.response.send_message(response, ephemeral=True)
            return

        try:
            await interaction.guild.kick(member, reason=motivo)
            embed = discord.Embed(title="Exclusão de Usuário", description=f"Usuário excluído: {member.mention}\nMotivo: {motivo}")
            embed.set_image(url=member.avatar.url)  # Define a imagem de perfil do usuário excluído
            await canal.send(embed=embed)
        except discord.Forbidden:
            response = f"Não foi possível banir o usuário {member.mention}. Não tenho permissão suficiente."
            await interaction.response.send_message(response, ephemeral=True)
            return

    else:
        response = "Nenhum usuário foi mencionado."
        await interaction.response.send_message(response, ephemeral=True)
        return

    response = f"O usuário {member.mention} foi expulso do servidor. Motivo: {motivo}"
    await interaction.response.send_message(response, ephemeral=True)










@tree.command(name="clear", description="Apaga mensagens")
@commands.has_permissions(administrator=True)
async def clear(interaction, quantidade: int):
    if quantidade <= 0 or quantidade > 10:
        response = "Apenas é possível apagar 10 mensagens por comando."
        await interaction.response.send_message(response)
        return

    messages = []
    async for message in interaction.channel.history(limit=quantidade):
        messages.append(message)

    await interaction.channel.delete_messages(messages)

    response = f"Excluídas {len(messages)} mensagens."
    await interaction.response.send_message(response, ephemeral=True)

@clear.error
async def clear_error(interaction, error):
    if isinstance(error, commands.MissingPermissions):
        response = "Somente administradores podem usar este comando."
        await interaction.response.send_message(response, ephemeral=True)


@tree.command(name="userclear", description="Apaga mensagens próprias")
async def userclear(interaction, quantidade: int):
    if quantidade <= 0 or quantidade > 10:
        response = "Apenas é possível apagar até 10 mensagens por comando."
        await interaction.response.send_message(response, ephemeral=False)
        return

    messages = []
    async for message in interaction.channel.history(limit=None):
        if message.author == interaction.user:
            messages.append(message)
            if len(messages) >= quantidade:
                break

    await interaction.channel.delete_messages(messages)

    response = f"{interaction.user.name} acabou de excluir {len(messages)} mensagens próprias."
    await interaction.response.send_message(response)


@tree.command(name="pic", description="Envia uma imagem")
async def pic(interaction, nome: str):
    with open('informacoes.json', 'r') as file:
        informacoes = json.load(file)

    if nome in informacoes:
        valores = informacoes[nome]
        valor_aleatorio = random.choice(valores)
        await interaction.response.send_message(valor_aleatorio)
    else:
        await interaction.response.send_message('Nome não encontrado.')

@tree.command(name="join", description="Entra em um canal de voz")
async def join(interaction):
    voice_client = discord.utils.get(bot.voice_clients, guild=interaction.guild)
    if interaction.user.voice and interaction.user.voice.channel:
        channel = interaction.user.voice.channel
        if voice_client and voice_client.is_connected():
            if voice_client.channel == channel:
                response = "Já estou conectado a este canal de voz."
                await interaction.response.send_message(response)
                return
            else:
                await voice_client.move_to(channel)
        else:
            voice_client = await channel.connect()

        response = f"Conectado ao canal de voz: {channel.name}"
        await interaction.response.send_message(response)
    else:
        await interaction.response.send_message('Você precisa estar em um canal de voz para usar este comando.')



@tree.command(name="leave", description="Sai do canal de voz")
async def leave(interaction):
    member = interaction.user
    voice_state = member.voice
    if voice_state and voice_state.channel:
        voice_client = discord.utils.get(bot.voice_clients, guild=interaction.guild)
        if voice_client and voice_client.is_connected():
            await voice_client.disconnect()
            await interaction.response.send_message('Desconectado da chamada de voz.', ephemeral=True)
        else:
            await interaction.response.send_message('Não estou conectado a um canal de voz.', ephemeral=True)
    else:
        await interaction.response.send_message('Você precisa estar em um canal de voz para usar este comando.', ephemeral=True)




@tree.command(name="play", description="Reproduz uma música")
async def play(interaction, audio_file: str):
    voice_client = discord.utils.get(bot.voice_clients, guild=interaction.guild)
    if interaction.user.voice and interaction.user.voice.channel:
        channel = interaction.user.voice.channel
        if voice_client and voice_client.is_connected():
            if voice_client.channel == channel:
                pass  # O bot já está conectado ao canal de voz atual
            else:
                await voice_client.move_to(channel)
        else:
            voice_client = await channel.connect()

        # Verificar se o bot já está reproduzindo música
        if voice_client.is_playing():
            response = "O bot já está reproduzindo uma música."
            await interaction.response.send_message(response)
            return

        # Verificar se o arquivo de áudio existe
        if not os.path.exists(audio_file):
            response = "O arquivo de áudio não foi encontrado."
            await interaction.response.send_message(response)
            return

        # Reproduzir música
        voice_client.play(discord.FFmpegPCMAudio(audio_file))

        response = f"Reproduzindo música: {audio_file}"
        await interaction.response.send_message(response, ephemeral=True)
    else:
        await interaction.response.send_message('Você precisa estar em um canal de voz para usar este comando.')



@client.event
async def on_ready():
    await tree.sync()

client.run('TOKEN')
