import discord
from discord.ui import Button, View
from discord.ext import commands
import requests
from discord import FFmpegPCMAudio  


intents = discord.Intents()
intents.message_content = True
intents.messages = True
intents.dm_messages = True
intents.voice_states = True
intents.members = True
intents.guild_messages = True
intents.guilds = True

# Giving bot appropriate intents

client = commands.Bot(command_prefix="+", intents=intents)


@client.event
async def on_ready():
    activity = discord.Game(name="For help | prefix = '+'", type=3)
    await client.change_presence(status=discord.Status.idle, activity=activity)
    print("Online 🟢")
    await client.wait_until_ready()

    # Ready confirmation and status with prefix tips

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.MissingRequiredArgument):
        embed2 = discord.Embed(
            title="**Error ⚠**", description=f"No word given to define."
        )
        await ctx.send(embed=embed2)
    
    # Catches no input error and sends appropriate message

@client.command(name = "define", aliases=["def"])
async def define(ctx, word):

    button = Button(label="Pronounciation", style=discord.ButtonStyle.green, emoji="🔉")
    view = View()
    view.add_item(button)

    # Defines button and adds it to view

    response = requests.get(f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}')
    data = response.json()

    # Searches up word from API and translates it from json format

    if isinstance(data, list) == False:
        embed2 = discord.Embed(
            title="**Error ⚠**", description=f"Could not find a definition for the word: '{word}'"
        )
        await ctx.send(embed=embed2)

        # Verifies if word is found in database

    else:
        wdata = data[0]
        phonetics = "N/A"
        for i in wdata['phonetics']:
            try:
                if i['text']:
                    phonetics = i['text']
            except:
                pass

        # Checks for all dictionaries in a list to find the phonetics
        # Default is set as N/A

        audio = ""
        for i in wdata['phonetics']:
            try:
                if i['audio']:
                    audio = i['audio']
            except:
                pass

        # Checks for all dictionaries in a list to find the audio link
        # Default is set as an empty string

        embed2 = discord.Embed(
            title=f"**{word.capitalize()}**",
            description=f"Phonetics: `{phonetics}`"
        )

        # Creates an Embed that acts as the starting point for all definitions

        meanings = len(wdata['meanings'])

        # Gets ammount of word types (Eg. Noun, Verb, Adverb, Adjective...)

        for k in range(meanings):
            meaning = wdata['meanings'][k]
            definitions = "\n- ".join(["", *[i['definition'] for i in meaning['definitions']]][0:5])

            # Uses list comprehension and joins the list to create an ordered string of definitions
            # Cuts of definitions at the first five values due to character limit

            synonyms = ", ".join(wdata['meanings'][k]['synonyms'])
            if synonyms == "":
                embed2.add_field(name=f"**{meaning['partOfSpeech'].capitalize()}**", value=f"Definition\n```{definitions}```")
            else:
                embed2.add_field(name=f"**{meaning['partOfSpeech'].capitalize()}**", value=f"Definition\n```{definitions}```\n\n Synonyms:\n```{synonyms}```")
        
        # Creates fields containing definitions (and synonyms if found) for each word type

        async def button_callback(interaction):

            # Defines the function to run on button callback

            if (ctx.author.voice):
                channel = ctx.message.author.voice.channel

                # Checks if user is in a voice channel

                try:
                    voice = await channel.connect()
                    source = FFmpegPCMAudio(f'{audio}', executable='ffmpeg')
                    player = voice.play(source, after=None)

                    # Attempts to join same vc as user and then plays audio file

                except:

                    # If bot is already connected to a vc, gets the Voice Client and plays audio file

                    voice = client.voice_clients[0]
                    source = FFmpegPCMAudio(f'{audio}', executable='ffmpeg')
                    player = voice.play(source, after=None)
            else:
                await ctx.send("Please join a Voice Channel First")

        button.callback = button_callback

        # Associates button callback to function

        # Adds button to embed if an audio file is present

        if audio == "":
            await ctx.send(embed=embed2)
        else:
            await ctx.send(embed=embed2, view=view)
    
        


client.run(TOKEN)

