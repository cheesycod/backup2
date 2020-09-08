import discord
import sqlite3
import config
import time
import re
from discord.ext import commands
from discord.utils import get
db = sqlite3.connect("automod.db")
pcur = db.cursor()
pcur.execute("CREATE TABLE IF NOT EXISTS logs (logid TEXT NOT NULL, user TEXT NOT NULL, action TEXT NOT NULL, message TEXT NOT NULL, word TEXT NOT NULL)")
pcur.execute("CREATE TABLE IF NOT EXISTS action_amount (logid TEXT NOT NULL, user TEXT NOT NULL, amount INTEGER)")
pcur.execute("CREATE TABLE IF NOT EXISTS actions (logid TEXT NOT NULL, user TEXT NOT NULL, punishment TEXT NOT NULL, message TEXT NOT NULL, reason TEXT NOT NULL)")
db.commit()
badwords = config.badwords
client = commands.Bot(command_prefix="%")
bypass = config.bypass
@client.event
async def on_ready():
    for guild in client.guilds:
        role_community = get(guild.roles, id=734869160441675820)    
        for channel in guild.channels:
                await channel.set_permissions(role_community, read_messages=False, send_messages=False)
@client.event
async def on_message(message):
    if(message.channel.id == 734869160454258886):
        time.sleep(0.3)
        await message.delete()
        return
    if(message.author.bot):
        return
    if(message.author.guild_permissions.administrator):
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
                community_role = discord.utils.get(message.guild.roles, name="Community")
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

@client.command()
async def mmode(ctx):
    args = ctx.message.content.split()
    if(len(args) != 2):
        await ctx.message.channel.send("**Invalid Operation for command mmap**")
        return
    fta = get(ctx.guild.roles, id=734869160445607973)
    ftb = get(ctx.guild.roles, id=734869160445607972)
    tac = [741589925383766106, 741640670791598110]
    tbc = [741589952877428757, 741645212652404847]
    if(args[1].lower() == "on"):
        role_community = get(ctx.guild.roles, id=734869160441675820)
        print(role_community)
        # 741583781764530227
        bcl = [734869161720938526, 734869161976791157, 735515833677119498, 736456818586550362, 741583781764530227, 735715550189191308, 738992674270609489]
        for channel in ctx.guild.channels:
            print(str(channel))
            if(channel.id == "748198512059088907" or channel.id == 748198512059088907):
                await channel.set_permissions(role_community, send_messages=True)
                continue
            if(channel.id == "734869160454258886" or channel.id == 734869160454258886):
                continue
            if(channel.category_id == 741583781764530227):
                if(channel.id in tac):
                    await channel.set_permissions(fta, send_messages=False)
                elif(channel.id in tbc):
                    await channel.set_permissions(ftb, send_messages=False)
                else:
                    await channel.set_permissions(fta, send_messages=False)
                    await channel.set_permissions(ftb, send_messages=False)
            if(channel.category_id in bcl):
                continue
            else:
                await channel.set_permissions(role_community, send_messages=False)
                print(f"DONE WITH {str(channel)}")
        await ctx.message.channel.send("MMODE is now on")
    elif(args[1].lower() == "off"):
        role_community = get(ctx.guild.roles, id=734869160441675820)
        bcl = [734869161720938526, 734869161976791157, 735515833677119498, 736456818586550362, 741583781764530227, 735715550189191308, 738992674270609489]
        for channel in ctx.guild.channels:
            if(channel.id == "748198512059088907" or channel.id == 748198512059088907):
                await channel.set_permissions(role_community, send_messages=False)
                continue
            if(channel.id == 734869160454258886 or channel.id == 738920073351397466 or channel.id == 741725992179204166 or channel.id == 743792950789668924):
                continue
            if(channel.category_id == 741583781764530227):
                if(channel.id in tac):
                    await channel.set_permissions(fta, send_messages=True)
                elif(channel.id in tbc):
                    await channel.set_permissions(ftb, send_messages=True)
                else:
                    await channel.set_permissions(fta, send_messages=True)
                    await channel.set_permissions(ftb, send_messages=True)

            if(channel.category_id in bcl):
                continue
            else:
                await channel.set_permissions(role_community, send_messages=True)
        await ctx.message.channel.send("MMODE is now off")
    else:
        await ctx.message.channel.send("**Invalid Operation for command mmap**")











client.run(config.token)
