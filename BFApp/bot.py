import discord
import time
import re
from discord.ext import commands
from discord.utils import get
client = commands.Bot(command_prefix = "%")
token = "NzIxMjc5NTMxOTM5Mzk3Njcz.XuSN6Q.A72q6Z9FOVrVOahNr3XSjO-zeh4"
sapp = 749733505910440011
gid = 722642206082465864

@client.command()
async def apply(message):
    cm = message.author
    if(message.author.bot):
        return
    guild = client.get_guild(gid)
    if(guild == None):
        return
    channel = guild.get_channel(sapp)
    if(channel == None):
        return
    await message.channel.send("Started your application, good luck!!!")
    await message.author.send("**Hi there! To start with, please type in your first name (first name only please).**")
    msg01 = await client.wait_for('message', check=lambda message: message.author == cm)
    await message.author.send("**Next, please type in your age.**")
    msg02 =  await client.wait_for('message', check=lambda message: message.author == cm)
    await message.author.send("**What is your gender?**")
    msg03 =  await client.wait_for('message', check=lambda message: message.author == cm)
    await message.author.send("**What is your timezone?**")
    msg04 =  await client.wait_for('message', check=lambda message: message.author == cm)
    await message.author.send("**What do you do when a staff member disagrees with you?**")
    msg05 =  await client.wait_for('message', check=lambda message: message.author == cm)
    await message.author.send("**What do you do when someone keeps breaking the rules within then minutes and have been warned by staff?**")
    msg06 =  await client.wait_for('message', check=lambda message: message.author == cm)
    await message.author.send("**How do you pour your cereal in milk?**")
    msg07 =  await client.wait_for('message', check=lambda message: message.author == cm)
    await message.author.send("Going to submit. Type submit to submit or cancel (or any invalid response) to cancel.")
    sb =  await client.wait_for('message', check=lambda message: message.author == cm)
    if(sb.content.lower() == "submit"):
        msg01 = msg01.content
        msg02 = msg02.content
        msg03 = msg03.content
        msg04 = msg04.content
        msg05 = msg05.content
        msg06 = msg06.content
        msg07 = msg07.content
        await channel.send(f"**Staff Application for {str(message.author)}**\n**First name:** {msg01}\n**Age:** {msg02}\n**Gender:** {msg03}\n**Timezone:** {msg04}")
        await channel.send(f"**What do they do when a staff member disagrees with them?** {msg05}")
        await channel.send(f"**What do they do when someone keeps breaking the rules with ten minutes and have been warned multiple times?** {msg06}")
        await channel.send(f"**How do they pour their milk in the cereal?** {msg07}")
        await message.author.send("Submitted your application successfully. Thank you and have a good day!")
    else:
        await message.author.send("Stopped your application either due to an invalid response or due to a stop request")
        return
client.run(token)
