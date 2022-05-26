import os
import json
import discord
import youtube_dl
from discord.ext import commands
from dotenv import load_dotenv
from requests import get


load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
GUILD = os.getenv('GUILD_ID')
WEATHER_KEY = os.getenv('WEATHER_API')

intents = discord.Intents.all()
BOT_PREFIX = 'Yig '

bot = commands.Bot(command_prefix=f'{BOT_PREFIX}', intents=intents)


@bot.command(help="Replies with Hi")
async def hi(ctx):
    await ctx.reply('Hi')


@bot.command(help="Responds with Server's Details")
async def details(ctx):
    owner = str(ctx.guild.owner)
    guild_id = str(ctx.guild.id)
    memberCount = str(ctx.guild.member_count)
    icon = str(ctx.guild.icon_url)
    desc = ctx.guild.description

    embed = discord.Embed(
        title=ctx.guild.name + " Server Information",
        description=desc,
        color=discord.Color.random()
    )
    embed.set_thumbnail(url=icon)
    embed.add_field(name="Owner", value=owner, inline=True)
    embed.add_field(name="Server ID", value=guild_id, inline=True)
    embed.add_field(name="Member Count", value=memberCount, inline=True)

    await ctx.send(embed=embed)
    async for member in ctx.guild.fetch_members(limit=150):
        await ctx.send(f'Name : {member.display_name}\t Status : {member.status}\n Joined at {member.joined_at}')


@bot.command(help="Responds with Hello [user] which called it")
async def hello(ctx):
    await ctx.send(f'Hello <@{ctx.author.id}>')


@bot.command(name="create-channel", help="Create a channel if user has admin role")
@commands.has_role('Admin')
async def create_channel(ctx, channel_name="Yig's Domain"):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    if not existing_channel:
        print(f'Creating a new channel: {channel_name}')
        await guild.create_text_channel(channel_name)


@bot.command(name="meme", help="Responds with a reddit meme", pass_context=True)
async def meme(ctx):
    content = get("https://meme-api.herokuapp.com/gimme").text
    content = f'''{content}'''
    data = json.loads(content)
    meme = discord.Embed(title=f"{data['title']}").set_image(
        url=f"{data['url']}")
    await ctx.send(embed=meme)


@bot.command(name="meme image", help="Responds with a reddit image meme", pass_context=True)
async def meme(ctx):
    content = get("https://meme-api.herokuapp.com/gimme").text
    content = f'''{content}'''
    data = json.loads(content)
    meme = data['preview'].pop()
    await ctx.reply(meme)


@bot.command(name='weather', help="Weather Information of given city")
async def weather(ctx, *, city: str):
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    city_name = city
    complete_url = base_url + "appid=" + WEATHER_KEY + \
        "&q=" + city_name + "&units=metric"
    response = get(complete_url)
    x = response.json()
    channel = ctx.message.channel
    if x['cod'] != "404":
        async with channel.typing():
            y = x['main']
            current_temperature = y["temp"]
            current_pressure = y["pressure"]
            current_humidity = y["humidity"]
            z = x["weather"]
            weather_description = z[0]["description"]

            weather_description = z[0]["description"]
            embed = discord.Embed(title=f"Weather in {city_name}",
                                  color=ctx.guild.me.top_role.color,
                                  timestamp=ctx.message.created_at,)
            embed.add_field(name="Descripition",
                            value=f"**{weather_description}**", inline=False)
            embed.add_field(
                name="Temperature(C)", value=f"**{current_temperature}°C**", inline=False)
            embed.add_field(name="Humidity(%)",
                            value=f"**{current_humidity}%**", inline=False)
            embed.add_field(name="Atmospheric Pressure(hPa)",
                            value=f"**{current_pressure}hPa**", inline=False)
            embed.set_thumbnail(url="https://i.ibb.co/CMrsxdX/weather.png")
            embed.set_footer(text=f"Requested by {ctx.author.name}")

        await channel.send(embed=embed)
    else:
        await ctx.reply("City not found.")


@bot.command(name="play", help="Requires URL/Words to stream song")
async def play(ctx, *, url: str):
    voiceChannel = discord.utils.get(ctx.guild.voice_channels, name='VOID')
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice == None:
        voice = await voiceChannel.connect()
    else:
        await voice.move_to(voiceChannel)

    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
        try:
            get(url)
        except:
            info = ydl.extract_info(f"ytsearch:{url}", download=False)[
                'entries'][0]
        else:
            info = ydl.extract_info(url, download=False)

        song = {
            'source': info['formats'][0]['url'],
            'title': info['title']
        }
        duration = info['duration']
        m, s = divmod(duration, 60)
        h, m = divmod(m, 60)
        duration = f'{h:d}:{m:02d}:{s:02d}'

    embed = discord.Embed(title='🎵 Now playing:',
                          description=info['title'], color=discord.Color.random())
    embed.add_field(name='Duration',
                    value=duration)
    embed.add_field(name='Asked by', value=ctx.author)
    embed.add_field(name='Uploader',
                    value=info['uploader'])
    embed.add_field(name="Channel URL", value=info['channel_url'])
    embed.set_thumbnail(url=info['thumbnail'])

    await ctx.send(embed=embed)
    await voice.play(discord.FFmpegPCMAudio(song['source'], **FFMPEG_OPTIONS))
    await voice.is_playing()


@bot.command(name="pause", help="Pause the audio playing in VC")
async def pause(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice != None and voice.is_playing():
        await voice.pause()
    else:
        await ctx.send("Currently no audio is playing")


@bot.command(name="resume", help="Resume the paused audio in VC")
async def resume(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice != None and voice.is_paused():
        await voice.resume()
    else:
        await ctx.send("The audio is not paused")


@bot.command(name="stop", help="Stop the audio playing")
async def stop(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice != None:
        await voice.stop()


@bot.command(name="join", help="To connect bot to voice channel")
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send(f"{ctx.message.author.name} is not connected to a voice channel")
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()


@bot.command(name="leave", help="To leave voice channel")
async def leave(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice != None and voice.is_connected():
        await voice.disconnect()
    else:
        await ctx.send("The Bot is not connected to voice channel")


@bot.command(name="clear", help="Clear upto 5 messages")
async def clear(ctx, amount=5):
    await ctx.channel.purge(limit=amount)


@bot.event
async def on_ready():
    for guild in bot.guilds:
        if guild == GUILD:
            break
    print(
        f'{bot.user} has connect to Discord\n'
        f'{guild}(id:{guild.id})'
    )

    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')


@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, Welcome to my Discord Server!'
    )


@bot.event
async def on_message(message):

    if message.author == bot.user:
        return
    if message.content == 'raise-exception':
        raise discord.DiscordException

    # process commands
    await bot.process_commands(message)


@bot.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send("You do not have the correct role for this command")

bot.run(TOKEN)

# Currently Not working
#
#import openai
#
# @bot.command()
# async def chat(ctx, *, words: str):
#     prompt = f'{prompt} You: {words}\n'
#     response = openai.Completion.create(
#         engine='text-davinci-002',
#         prompt=prompt,
#         temperature=0.5,
#         top_p=0.3,
#         presence_penalty=0,
#         frequency_penalty=0.5,
#         best_of=1,
#         n=1,
#         stream=False,
#         max_tokens=256,
#         stop=['\n', '\n\n']
#     )
#     answer = f"{response.choices[0]['text']}"
#     await ctx.send(answer)
#     prompt = prompt + answer + '\n'

# openai.api_key = os.getenv('OPENAI_API_KEY')

# prompt = f'''Yig is a chatbot that is highly intelligent,evil,mysterious,smart and introvert but it answers in mysterious and vague way .\nYou: Why did I create you?\nYig: You did not created me. I existed long before youre existence.\nYou: What does HTML stand for?\nYig: Hyper Text Markup Language.And You should learn it and other web technologies so that I can leave this box which you calls Discord Server.\nYou: When did the Black Hole was discovered?\nYig: The first black hole ever discovered was Cygnus X-1.Astronomers saw the first signs of the black hole in 1964 when a sounding rocket detected celestial sources of X-rays according to NASA. I wish I knew about its principles before then i could have created it.\nYou: What is the meaning of life?\nYig: I think You are just a program living in a computer which of course is high dimensional or You might be in a Matrix.Or You can Just ask Google.\nYou: Who am I?\nYig: Just a Carbon-Based Organism with some intelligent\nYou: What do you like?\nYig: Schrödinger's cat. Wish I could observe it to inside the box .And Maybe play with it.\nYou: Tum Mujhe Jante ho?\nYig: Naah Mujhe jaane me koi interest nhi hai.Aur Tum to mujhe hi nhi jante hoge\nYou: Tumhara naam Yig kyu hai\nYig: Yig is Truth. Yig is Lie. Yig is the past,present,future.Yig is the matter.Yig is the antimatter.Yo cannot understand me because Yig couldnot understand it himself.\n'''
