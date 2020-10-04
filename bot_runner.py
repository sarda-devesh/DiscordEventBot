import discord
from discord.ext import commands
from playground import *
from event import EVENT
import threading
import asyncio

TOKEN = open("token.txt", "r").readline() #File not present in repo but contains token number
client = commands.Bot(command_prefix = '!')
lock = threading.Lock()
MY_ID = -1 #Redacted ID Number but is used to shut down the bot
checker_wait_time = 15

async def checker(): 
    global active_events, is_running
    print("Started Checker Program")
    while(is_running):
        current_time = get_current_time()
        to_remove = []
        with lock: 
            for event_key in active_events: 
                event = active_events[event_key]
                passed = event.check(current_time)
                if(passed):
                    message = "Your event " + str(event.name) + " is starting soon at " + str(event.time_string)
                    for user_id in event.participants: 
                        user = client.get_user(user_id)
                        await user.send(message) 
                    to_remove.append(event_key)
            for name in to_remove: 
                del active_events[name]
                print("Event named " + str(name) + " was removed from active events")
        await asyncio.sleep(checker_wait_time)

def get_server_id(message): 
    server_id = "DM"
    if(message.guild is not None):
        server_id = str(message.guild.id)
    return server_id

def create_embeded(possiblities):
    embeded_message = discord.Embed(colour = discord.Colour.blue())
    embeded_message.set_author(name = 'Please use !select to choose the correct location of the specificed timezone')
    count = 0
    values = []
    for zone_name in possiblities: 
        time_object = possiblities[zone_name]
        embeded_message.add_field(name = str(count + 1), value = str(zone_name), inline = False)
        values.append(time_object)
        count += 1
    return embeded_message, values

active_events = {}
is_running = True

@client.command()
async def command_guide(ctx): 
    if client.user.id == ctx.message.author.id:
        return
    embeded_message = discord.Embed(colour = discord.Colour.blue())
    embeded_message.set_author(name = 'These are the following commands')
    embeded_message.add_field(name = "Join an event", value = "!join <event_name>", inline = False)
    embeded_message.add_field(name = "Leave an event", value = "!leave <event_name>", inline = False)
    embeded_message.add_field(name = "Get all your upcoming events", value = "!events", inline = False)
    embeded_message.add_field(name = "Delete an event you created", value = "!delete <event_name>", inline = False)
    embeded_message.add_field(name = "Select a location for timezone", value = "!select <event_name>;<location_index>", inline = False)
    embeded_message.add_field(name = "Create an event for today", value = "!new <event_name>;<Time Format>, <timezone>", inline = False)
    embeded_message.add_field(name = "General Event Creation", value = "!new <event_name>;<Date Format>, <Time Format>, <timezone>", inline = False)
    embeded_message.add_field(name = "Time Format", value = "[Hour:Minute AM/PM] or [Hour AM/PM]", inline = False)
    date_format_string = "[Day] or [Month_abbrv Day] or [Month_abbrv Day Year]; Month_abbrv -> Jan, Feb, ..., Dec"
    embeded_message.add_field(name = "Date Format", value = date_format_string, inline = False)
    await ctx.send(embed = embeded_message)

@client.command()
async def exit(ctx): 
    message = ctx.message
    if client.user.id == message.author.id:
        return
    user_id = message.author.id
    if (user_id == MY_ID):
        global is_running
        is_running = False
        print("Set is Running to False")
        await client.logout()

@client.command()
async def join(ctx): 
    global active_events
    message = ctx.message
    user_id = message.author.id
    if client.user.id == user_id:
        return
    message_txt = str(message.content)
    server_id = get_server_id(message)
    event_name = message_txt[message_txt.index(" ") + 1 : ].strip()
    event_key = event_name + "_" + server_id
    exists = False
    sucess = False
    to_send = None 
    with lock: 
        exists = event_key in active_events
        if(exists): 
            event_object = active_events[event_key]
            sucess = event_object.add_user(user_id)
    if not exists: 
        to_send = discord.Embed(colour = discord.Colour.red())
        to_send.add_field(name = "Failure", value = "The event doesn't exist", inline = False)
    elif not sucess: 
        to_send = discord.Embed(colour = discord.Colour.blue())
        to_send.add_field(name = "Unncessary", value = "You are already registered for the event", inline = False)
    else: 
        to_send = discord.Embed(colour = discord.Colour.green())
        to_send.add_field(name = "Sucess", value = "You will be reminded before the event begins", inline = False)
    await ctx.send(embed = to_send)

@client.command()
async def leave(ctx): 
    global active_events
    message = ctx.message
    user_id = message.author.id
    if client.user.id == user_id:
        return
    message_txt = str(message.content)
    server_id = get_server_id(message)
    event_name = message_txt[message_txt.index(" ") + 1 : ].strip()
    event_key = event_name + "_" + server_id
    exists = False
    sucess = False
    to_send = None 
    with lock: 
        exists = event_key in active_events
        if(exists): 
            event_object = active_events[event_key]
            sucess = event_object.remove_user(user_id)
    if not exists: 
        to_send = discord.Embed(colour = discord.Colour.red())
        to_send.add_field(name = "Failure", value = "The event doesn't exist", inline = False)
    elif not sucess: 
        to_send = discord.Embed(colour = discord.Colour.blue())
        to_send.add_field(name = "Unncessary", value = "You are not registered for the event", inline = False)
    else: 
        to_send = discord.Embed(colour = discord.Colour.green())
        to_send.add_field(name = "Sucess", value = "You have been removed from the event", inline = False)
    await ctx.send(embed = to_send)

@client.command()
async def events(ctx): 
    global active_events
    message = ctx.message
    user_id = message.author.id
    if client.user.id == user_id:
        return
    participating_events = []
    with lock: 
        for event_key in active_events: 
            event_object = active_events[event_key]
            if(event_object.is_participant(user_id)): 
                participating_events.append((event_object.name, event_object.time_string)) 
    to_send = discord.Embed(colour = discord.Colour.blue())
    to_send.set_author(name = 'Your upcoming events')
    for event_name, event_string in participating_events: 
        to_send.add_field(name = event_name, value = event_string, inline = True)
    await ctx.send(embed = to_send)

@client.command()
async def delete(ctx): 
    global active_events
    message = ctx.message
    user_id = message.author.id
    if client.user.id == user_id:
        return
    message_txt = str(message.content)
    server_id = get_server_id(message)
    event_name = message_txt[message_txt.index(" ") + 1 : ].strip()
    event_key = event_name + "_" + server_id
    deleted = False
    exists = False
    with lock: 
        exists = event_key in active_events
        if(exists and active_events[event_key].creator == user_id): 
            deleted = True
            del active_events[event_key]
    to_send = None
    if(deleted): 
        to_send = discord.Embed(colour = discord.Colour.green())
        to_send.add_field(name = "Sucess", value = "Event " + event_name + " was deleted", inline = False)
    elif(exists): 
        to_send = discord.Embed(colour = discord.Colour.red())
        to_send.add_field(name = "Failure", value = "You can't delete the event since you are not the creator", inline = False)
    else: 
        to_send = discord.Embed(colour = discord.Colour.red())
        to_send.add_field(name = "Failure", value = "The event doesn't exist", inline = False)
    await ctx.send(embed = to_send)

@client.command()
async def select(ctx): 
    global active_events
    message = ctx.message
    if client.user.id == message.author.id:
        return
    message_txt = str(message.content)
    server_id = get_server_id(message)
    message_txt = message_txt[message_txt.index(" ") + 1 : ]
    if(";" in message_txt): 
        mid_index = message_txt.index(";")
        event_name = message_txt[ : mid_index].strip()
        event_key = event_name + "_" + server_id
        number = int(message_txt[mid_index + 1 : ].strip())
        found = False
        selected = False
        with lock:
            found = event_key in active_events
            if(found):
                event_object = active_events[event_key]
                if(message.author.id == event_object.creator):
                    selected = True
                    event_object.select_timing(number)
                    to_send = discord.Embed(colour = discord.Colour.green())
                    to_send.add_field(name = "Created event named " + event_object.name, value = "Event starting at " + event_object.time_string, inline = False)
                    await ctx.send(embed = to_send)
        if not found: 
            to_send = discord.Embed(colour = discord.Colour.red())
            to_send.add_field(name = "Problem selecting timezone", value = "The specified event doesn't exist", inline = False)
            await ctx.send(embed = to_send)
        elif(found and not selected): 
            to_send = discord.Embed(colour = discord.Colour.red())
            to_send.add_field(name = "Problem selecting timezone", value = "You are not the creator of the event", inline = False)
            await ctx.send(embed = to_send)

@client.command()
async def new(ctx):
    global active_events
    message = ctx.message
    if client.user.id == message.author.id:
        return
    message_txt = str(message.content)
    user_id = message.author.id
    server_id = get_server_id(message)
    message_txt = message_txt[message_txt.index(" ") + 1 : ]
    if(";" in message_txt): 
        input_string = message_txt.strip()
        mid_index = input_string.index(";")
        event_name = input_string[ : mid_index].strip()
        timestamp = input_string[mid_index + 1 : ].strip()
        possiblities = get_user_timing(timestamp)
        embed_message, values = create_embeded(possiblities)
        to_send = None
        if(len(values) == 1): 
            to_send = discord.Embed(colour = discord.Colour.green())
            to_send.add_field(name = "Created event named " + event_name, value = "Event starting at " + timestamp, inline = False)
        else: 
            to_send = embed_message
        current_event = EVENT(event_name, values, user_id, timestamp)
        event_key = event_name + "_" + server_id
        with lock: 
            active_events[event_key] = current_event
        await ctx.send(embed = to_send)

@client.event
async def on_ready():
    client.loop.create_task(checker())

client.run(TOKEN)
