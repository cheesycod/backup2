import discord
import os
import sqlite3
import config
import time
import re
from captcha.image import ImageCaptcha
from discord.ext import commands
from discord.utils import get
db = sqlite3.connect("automod.db")
pcur = db.cursor()
pcur.execute("CREATE TABLE IF NOT EXISTS logs (logid TEXT NOT NULL, user TEXT NOT NULL, action TEXT NOT NULL, message TEXT NOT NULL, word TEXT NOT NULL)")
pcur.execute("CREATE TABLE IF NOT EXISTS action_amount (logid TEXT NOT NULL, user TEXT NOT NULL, amount INTEGER)")
pcur.execute("CREATE TABLE IF NOT EXISTS actions (logid TEXT NOT NULL, user TEXT NOT NULL, punishment TEXT NOT NULL, message TEXT NOT NULL, reason TEXT NOT NULL)")
pcur.execute("CREATE TABLE IF NOT EXISTS captcha (uid INTEGER, captcha TEXT NOT NULL)")
db.commit()
badwords = config.badwords
client = commands.Bot(command_prefix="%")
bypass = config.bypass
#@client.event
#async def on_command_error(arg1, error):
#    pass
@client.event
async def on_message(message):
    if message.channel.type is discord.ChannelType.private: 
        return
    if(message.channel.id == 748268086209019984):
        time.sleep(0.3)
        await message.delete()
        if(message.content == "%verify"):
            print("BYPASS")
            await client.process_commands(message)
            return
        else:
            return
    if(message.author.bot):
        return
    if(message.author.guild_permissions.administrator):
        print("BYPASS")
        await client.process_commands(message)
    if(bypass == 1):
        return
    # Sanitize the message
    msg_real = message.content
    message.content = re.sub('[^A-Za-z0-9]+', '', message.content)
    # Get a logid
    used_id = pcur.execute(f"SELECT logid from logs")
    used_id = used_id.fetchall()
    used_ids = []
    logid = None
    a = 1
    for i in used_id:
        num = i[0]
        used_ids.append(int(num))
    while(logid == None):
        if(a in used_ids):
            a+=1
        else:
            logid = a
    for word in badwords:
        reason = "BANNED_WORD"
        if(message.content.__contains__(word.lower())):
            # Log it in the database
            print(f"INSERT INTO logs VALUES ('{str(logid)}', '{str(message.author.id)}', '{reason}', 'STRING_ESCAPE({msg_real})', '{word}')")
            pcur.execute(f"INSERT INTO logs VALUES ('{str(logid)}', '{str(message.author.id)}', '{reason}', '{message.content}', '{word}')")
            # Update and get the current punishment amount
            amc = pcur.execute(f"SELECT amount from action_amount WHERE user = {str(message.author.id)}")
            amc = amc.fetchall()
            try:
                amc = amc[0][0]
                pcur.execute(f"DELETE FROM action_amount WHERE user = {str(message.author.id)}")
                pcur.execute(f"INSERT INTO action_amount VALUES ('{str(logid)}', '{str(message.author.id)}', '{int(amc + 1)}')")
                amc = amc + 1
                print(amc)
            except:
                amc = 0
                pcur.execute(f"INSERT INTO action_amount VALUES ('{str(logid)}', '{str(message.author.id)}', '{int(amc + 1)}')")
                amc = amc + 1
            # Default Delete And DM Action
            pcur.execute(f"INSERT INTO actions VALUES ('{str(logid)}', '{str(message.author.id)}', 'DELETE_DM', '{message.content}', '{reason}')")
            db.commit()
            await message.delete()
            # Send the DM
            try:
                await message.author.send(f"**Your message was deleted automatically**\n'{msg_real}' has been autodeleted for containing banned word '{word}'.\nYour automod count is now {amc}")
                pcur.execute(f"INSERT INTO logs VALUES ('{str(logid)}', '{str(message.author.id)}', 'DM_SUCCESS', '{message.content}', '{word}')")
            except:
                pcur.execute(f"INSERT INTO logs VALUES ('{str(logid)}', '{str(message.author.id)}', 'DM_FAILED', '{message.content}', '{word}')")
                await message.channel.send(f"**Your message was deleted automatically**\n'{msg_real}' has been autodeleted for containing banned word '{word}'.\nYour automod count is now {amc}")

            if(amc > 7):
                # Automod Action
                pcur.execute(f"INSERT INTO actions VALUES ('{str(logid)}', '{str(message.author.id)}', 'AUTOMODDED', '{message.content}', '{reason}')")
                automod_role = discord.utils.get(message.guild.roles, name="Automodded")
                community_role = discord.utils.get(message.guild.roles, name="Verified")
                await message.author.add_roles(automod_role)
                await message.author.remove_roles(community_role)
        db.commit()
@client.event
async def on_voice_state_update(member, before, after):
    if not before.channel and after.channel:
        role = discord.utils.get(member.guild.roles, name="In VC")
        await member.add_roles(role)
    elif before.channel and not after.channel:
        role = discord.utils.get(member.guild.roles, name="In VC")
        await member.remove_roles(role)
@client.command()
async def automods(ctx):
    # Get logid
    logid = pcur.execute(f"SELECT logid from actions WHERE user = {str(ctx.message.author.id)}")
    logid = logid.fetchall()
    try:
        loglist = []
        for id in logid:
            if(id[0] in loglist):
                continue
            loglist.append(id[0])
        print(loglist)
    except:
        print("No logid found")
import secrets
import string
global font
font = []
for f in os.listdir("data"):
    font.append("data/" + f)

@client.command()
async def verify(ctx):
    community_role = discord.utils.get(ctx.message.guild.roles, name="Verified")
    message = ctx.message
    mauth = message.author
    print(mauth)
    if(ctx.message.channel.id != 748268086209019984):
        return
    t = 1
    while(t < 4):
        secret = ""
        for i in range(0, 5):
            secret += secrets.choice(string.ascii_uppercase + string.digits)
        print(secret)
        image = ImageCaptcha(fonts=font)
        dis = image.generate(secret)
        await ctx.message.author.send("**Hi there! To verify into the server, please answer the following captcha to prove that you are human.**")
        await ctx.message.author.send(file=discord.File(dis, f'captcha{ctx.message.author.id}.png'))
        try:
            msg = await client.wait_for('message', check=lambda message: str(message.channel.type) == "private", timeout = 20)
        except:
            await ctx.message.author.send("Captcha timed out. Please reverify to try again!")
            return
        if(msg.content.lower() == secret.lower()):
            print("OK")
            await msg.author.send("To finish verifying, please tell me how many rules **(count the bullet points; exclude punishments and other non bulleted rules)** there are in this server?\nNote: Answers that are one or two off will still be accepted")
            try:
                msg = await client.wait_for('message', check=lambda message: message.author == mauth, timeout = 32)
            except:
                await ctx.message.author.send("Captcha timed out. Please reverify to try again!")
            try:
                it = int(msg.content)
            except:
                await msg.author.send("Your answer is not a number. Please redo the captcha and try again")
                await msg.author.send(f"Incorrect Captcha\nPlease try again\nAttempt: {str(t)}\nAmount of tries remaining: {str(3 - t)}")
                t+=1
                continue
            if it in range(20, 24):
                await msg.author.send("Bristlefrost, Rootspring and Shadowsight have successfully verified you into the server.\n*P.S.* BristleRoot is the best Warrior Cats ship ever!!")
                await ctx.message.author.add_roles(community_role)
                return
            else:
                await msg.author.send("Invalid response\nPlease reread the rules and try doing the captcha again")
                await msg.author.send(f"Incorrect Captcha\nPlease try again or reverify to get more tries\nAttempt: {str(t)}\nAmount of tries remaining: {str(3 - t)}")
                t+=1
                continue
        else:
            if(3 - t < 0):
                await ctx.message.author.send("Invalid response\nPlease reread the rules and try doing the captcha again")
                return
            else:
                await ctx.message.author.send(f"Incorrect Captcha\nPlease try again\nAttempt: {str(t)}\nAmount of tries remaining: {str(3 - t)}")
            t+=1
            continue
client.run(config.token)
