import discord
import os
import itertools
import copy
import random
import asyncio
from replit import db
# from keep_alive import keep_alive
from discord.ext import commands
# from dotenv import load_dotenv

# actual logic
# Player Object
players = []
queue = None
commands_string = "?register\n?join\n?unjoin\n?start\n?queue\n?help\n------- Using Valorant Autobalance -------\n?team1\n?team2\n?noteam\n?move\n?unmove\n?randommap\n?cleanteam"
team1list = []
team2list = []
rank_dict = {
      'iron': 0,
      'bronze': 300,
      'silver': 600,
      'gold': 900,
      'platinum': 1200,
      'plat': 1200,
      'diamond': 1500,
      'immortal': 1800,
      'radiant': 1800
  }

class Player:
    def __init__(self, user, mmr):
        self.user = user
        self.mmr = mmr

    def __repr__(self):
        return "Player: {0}, MMR: {1}".format(self.user, self.mmr)


# Return the complement of sublist from my_list
def complement(sublist, my_list):
    complement = my_list[:]
    for x in sublist:
        complement.remove(x)
    return complement


# Absolute value of difference
def difference(sublist1, sublist2):
    return abs(sum(sublist1) - sum(sublist2))

# not used
def join_players(username, rank, division, rr):
    global players
    mmr = rank_dict[rank] + (int(division) - 1) * 100 + int(rr)

    new_player = Player(username, mmr)

    if new_player not in players:
        players.append(new_player)

    # # may have to change with discord api
    # while len(players) < 10:
    #     user = input("Enter your username or type 'done' to finish: ")
    #     if user=='done':
    #         break
    #     rank = input('Enter your rank: ').lower()
    #     if rank == "immortal" or rank=="radiant":
    #         rr = input('Enter your RR: ')
    #         mmr = rank_dict[rank] + int(rr)
    #     else:
    #         division = input('Enter your division: ')
    #         rr = input('Enter your RR: ')
    #         mmr = rank_dict[rank] + (int(division)-1)*100 + int(rr)
    #     players.append(Player(user,mmr))
    #     # print(players)
    # return players

def calculate_rank(mmr):
  mmr_dict = rank_dict.values()
  mmr_list = []

  for x in mmr_dict:
    if x <= mmr:
      mmr_list.append(x)

  rank_value = max(mmr_list)

  for key, value in rank_dict.items():
      if value == rank_value:
          rank = key

  if rank == "immortal" or rank == "radiant":
    rr = mmr - rank_value
    return "radiant / immortal " + str(rr) + " RR"
  else:
    division = int((mmr - rank_value) / 100) + 1
    output_string = rank + " " + str(division)
    return output_string


def calculate_mmr(rank, division, rr):
    rank = rank.lower().strip()
    mmr = rank_dict[rank] + (int(division) - 1) * 100 + int(rr)
    return mmr


def dict_copy(dict_og):
    new_dict = copy.deepcopy(dict_og)
    return new_dict


def calculate_teams(players):
    mmr_list = []
    mmr_dict_og = {}
    mmr_dict = {}

    # loop through players list and append to mmr list
    for player in players:
        mmr_list.append(player.mmr)
        # append to player dictionary
        if player.mmr in mmr_dict_og:
            mmr_dict_og[player.mmr].append(player)
        else:
            mmr_dict_og[player.mmr] = [player]

    lower_difference = sum(mmr_list)
    team1_list, team2_list = [], []
  
    for partition in itertools.combinations(mmr_list, 5):
        # print("this is mmr_dict_og "+ str(mmr_dict_og))

        # mmr_dict = dict_copy(mmr_dict_og)
        # mmr_dict = copy.deepcopy(mmr_dict_og)
        # mmr_dict = mmr_dict_og.copy()
        for player in players:
            if player.mmr in mmr_dict:
                mmr_dict[player.mmr].append(player)
            else:
                mmr_dict[player.mmr] = [player]

        # print("this is mmr_dict "+ str(mmr_dict))
        partition = list(partition)
        remainder = complement(partition, mmr_list)

        diff = difference(partition, remainder)

        #if diff < lower_difference:
        team_pairs=[]
        if diff < 300:
          lower_difference = diff
          team1 = []
          team2 = []
          for mmr in partition:
              team1.append(mmr_dict[mmr].pop())
          for mmr in remainder:
              team2.append(mmr_dict[mmr].pop())
          team_pairs.append([team1, team2, lower_difference])
        
    return random.choice(team_pairs)          



# pick map
def pick_map(bans=[]):
    maps = ['Ascent', 'Split', 'Icebox', 'Bind', 'Breeze', 'Haven', 'Fracture']
    number = random.randrange(6)
    while maps[number] in bans:
        number = random.randrange(6)
    return maps[number]


def map_image(map):
    maps_dict = {
        'Ascent':
        'https://images.contentstack.io/v3/assets/bltb6530b271fddd0b1/blt930666d9ab927326/5eabe9c45751b2150e57a42c/ascent1.jpg?auto=webp&width=915',
        'Split':
        'https://images.contentstack.io/v3/assets/bltb6530b271fddd0b1/bltdfd43bd79d9b3410/5eabe9fea20afe612d82f833/split3.jpg?auto=webp&width=915',
        'Icebox':
        'https://images.contentstack.io/v3/assets/bltb6530b271fddd0b1/blt9ef7b41910a14118/5f80debff6c586323f8b17a3/icebox_1.jpg?auto=webp&width=915',
        'Bind':
        'https://cdn1.dotesports.com/wp-content/uploads/2020/12/09115318/Bind-VAL.jpeg',
        'Breeze':
        'https://cdn1.dotesports.com/wp-content/uploads/2021/04/26034733/Breeze-2-1-1536x864.jpg',
        'Haven':
        'https://cdn1.dotesports.com/wp-content/uploads/2020/06/30204333/Loading_Screen_Haven-1536x864.png',
      'Fracture':
      'https://static.wikia.nocookie.net/valorant/images/f/fc/Loading_Screen_Fracture.png/revision/latest?cb=20210908143656'
    }

    return maps_dict[map]


# random side
def pick_side():
    number = random.randrange(2)
    if number == 0:
        return 'Team 1 is attacking first'
    else:
        return 'Team 2 is attacking first'


# to print in embed
def list_to_string(list):
    output_string = ""
    for x in list:
        output_string += x
        output_string += "\n"
    return output_string


def team_to_list(list):
    output_string = ""
    for x in list:
        output_string += str(x.user)
        output_string += "\n"
    return output_string


def clear():
    global players, queue
    players.clear()
    queue = None


def win_perc(sublist1, sublist2):
    team1 = 0
    team2 = 0
    print(sublist1)
    for player in sublist1:
        team1 += player.mmr
    for player in sublist2:
        team2 += player.mmr
    total = team1 + team2
    team1_percentage = team1 / total
    print(team1_percentage)
    team2_percentage = team2 / total
    print(team2_percentage)
    print("{:.0%}".format(team1_percentage))
    print("{:.0%}".format(team2_percentage))


example_players = [
    Player('kwan#6718', 1600),
    Player('San#8311', 1020),
    Player('jae#4907', 1430),
    Player('SealableBox845#0025', 882),
    Player('matthieus#1049', 1210),
    Player('Nodnarb#5845', 860),
    Player('maaaaaasha#4255', 940),
    Player('ddo ppi#5411', 453),
    Player('nickgo1#9039', 1900),
    Player('peetskeet#9810', 1025)
]
# players = get_players()
# team1, team2, diff = calculate_teams(example_players)

# print('Team 1:')
# for player in team1:
#     print(player)
# print('\nTeam 2:')
# for player in team2:
#     print(player)
# #print('\nMMR Difference: ' + str(diff))

# print('\nMap is: ' + pick_map())
# print('\n' + pick_side())

# Discord API
# client = discord.Client()
bot = commands.Bot(command_prefix='?', help_command=None)
# load_dotenv()
TOKEN = os.getenv('TOKEN')

# bot = commands.Bot(command_prefix='!')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.message.channel.send("No such command", delete_after=10)
        await ctx.message.delete()
    else:
        # print("u bozo")
        raise error


@bot.event
async def on_ready():
    # print('We have logged in as {0.user}'.format(bot))
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    text_channel_list = []
    voice_channel_list = []
    for guild in bot.guilds:
        for channel in guild.text_channels:
            text_channel_list.append(channel)
    print(text_channel_list)

    for guild in bot.guilds:
        for channel in guild.voice_channels:
            voice_channel_list.append(channel)
    print(voice_channel_list)

    welcome_embed = discord.Embed(
        title="Welcome to the x-mans Bot",
        description="Please use ?help to get the list of commands")
    welcome_embed.add_field(name="Commands", value=commands_string)

    channel_id = bot.get_channel(855979807370903575)
    await channel_id.send(embed=welcome_embed)

@bot.command()
async def asdf(ctx):
  print(calculate_rank(940))
  print(calculate_rank(890))


@bot.command()
async def help(ctx):
    await ctx.message.delete()

    #help embed
    help_embed = discord.Embed(
        title="Welcome to the x-mans Bot",
        description="This bot is made to organize a custom game")
    help_embed.add_field(name="Commands", value=commands_string)

    await ctx.send(embed=help_embed, delete_after=20)

@bot.command()
async def randommap(ctx):
  await ctx.message.delete()
  selected_map = str(pick_map())

  number = random.randrange(2)
  if number == 0:
      side = 'attacking'
  else:
      side = 'defense'

  output_string = str(ctx.author) + "'s team is on " + side

  if len(players) == 10:
    # match embed
    match_embed = discord.Embed(title=selected_map,
                                color=discord.Color.red())
    match_embed.add_field(name="Team 1",
                          value=team_to_list(team1),
                          inline=True)
    match_embed.add_field(name="Team 2",
                          value=team_to_list(team2),
                          inline=True)
    match_embed.set_footer(text=pick_side())
    match_embed.set_image(url=map_image(selected_map))
    game_info_embed = await ctx.send(embed=match_embed)
    refresh_emoji = "🔄"
    await game_info_embed.add_reaction(refresh_emoji)

    #refresh map
    await ctx.send(
        "You may react to change map and sides (10 seconds)",
        delete_after=10)

    try:
        reaction, member = await bot.wait_for(
            "reaction_add",
            check=lambda reaction, user: reaction.message.channel ==
            ctx.channel and user != bot.user and str(
                reaction.emoji) == refresh_emoji,
            timeout=10)

        if reaction:
            await game_info_embed.delete()
    except asyncio.TimeoutError:
        await game_info_embed.clear_reactions()
        # await refresh_info.delete()
        # return
              
  # map embed
  map_embed = discord.Embed(title=selected_map,
                              color=discord.Color.red())
  map_embed.set_footer(text=output_string)
  map_embed.set_image(url=map_image(selected_map))

  await ctx.send(embed=map_embed, delete_after=10)

@bot.command()
async def cleanteam(ctx):
  await ctx.message.delete()
  global team1list, team2list
  team1list, team2list = [], []

    # confirmation
  cleaned_embed = discord.Embed(title=str(ctx.author) +
                                   " has reset all teams.",
                                   description="Type ?team1 or ?team2 to join")
  
  await ctx.send(embed=cleaned_embed, delete_after=10)

@bot.command()
async def chooseteam(ctx):
  await ctx.message.delete()

  team_embed = discord.Embed(title="Pick a team",
                                         description="Team 1 or Team 2")
  team_picker = await ctx.send(embed=team_embed)
  await team_picker.add_reaction("1️⃣")
  await team_picker.add_reaction("2️⃣")

  # confirmation
  joined_embed = discord.Embed(title=str(ctx.author) +
                               " has joined the team.",
                               description="Type ?move to move to your channel")

  team_emoji = ["1️⃣", "2️⃣"]

  team1, team2 = [], []

  try:
      reaction, member = await bot.wait_for(
          "reaction_add",
          check=lambda reaction, user: reaction.message.channel ==
          ctx.channel and user != bot.user and str(reaction.emoji
                                                   ) in team_emoji)
  except asyncio.TimeoutError:
      await team_picker.delete()
      await ctx.send("Invalid", delete_after=10)
      # return

  for reaction in team_picker.reactions:
      if reaction.emoji == team_emoji[0]:
          async for user in reaction.users():
              #if user != client.user:
              print("this is working")
              temp_user = Player(user.name, 0)
              team1list.append(temp_user)
              await ctx.send(embed=joined_embed, delete_after=10)
              
      elif reaction.emoji == team_emoji[1]:
          async for user in reaction.users():
              #if user != client.user:
              temp_user = Player(user.name, 0)
              team2list.append(temp_user)
              await ctx.send(embed=joined_embed, delete_after=10)

  

@bot.command()
async def team1(ctx):
    await ctx.message.delete()

    # confirmation
    joined_embed = discord.Embed(title=str(ctx.author) +
                                 " has joined the team.",
                                 description="Type ?move to move to your channel")

    # confirmation
    already_in_embed = discord.Embed(title=str(ctx.author) +
                                     " is already in this team.",
                                     description="Type ?noteam to leave")

    for player in team1list:
        if player.user == ctx.author:
            await ctx.send(embed=already_in_embed, delete_after=10)
            return
    else:
        for player in team2list:
            if player.user == ctx.author:
                team2list.remove(player)
        temp_user = Player(ctx.author, 0)
        team1list.append(temp_user)
        await ctx.send(embed=joined_embed, delete_after=10)


@bot.command()
async def team2(ctx):
    await ctx.message.delete()

    # confirmation
    joined_embed = discord.Embed(title=str(ctx.author) +
                                 " has joined the team.",
                                 description="Type ?move to move to your channel")

    # confirmation
    already_in_embed = discord.Embed(title=str(ctx.author) +
                                     " is already in this team.",
                                     description="Type ?noteam to leave")

    for player in team2list:
        if player.user == ctx.author:
            await ctx.send(embed=already_in_embed, delete_after=10)
            return
    else:
        for player in team1list:
            if player.user == ctx.author:
                team1list.remove(player)
        temp_user = Player(ctx.author, 0)
        team2list.append(temp_user)
        await ctx.send(embed=joined_embed, delete_after=10)


@bot.command()
async def noteam(ctx):
    await ctx.message.delete()

    removed = False
    # removed
    removed_embed = discord.Embed(
        title=str(ctx.author) + " is no longer on a team.",
        description="Type ?team1 or ?team2 to join a team")
    # confirmation
    not_in_embed = discord.Embed(
        title=str(ctx.author) + " is not in a team.",
        description="Type ?team1 or ?team2 to join a team")

    for player in team1list:
        if player.user == ctx.author:
            team1list.remove(player)
            removed = True

    for player in team2list:
        if player.user == ctx.author:
            team2list.remove(player)
            removed = True

    if not removed:
        await ctx.send(embed=not_in_embed, delete_after=10)
    else:
        await ctx.send(embed=removed_embed, delete_after=10)


@bot.command()
async def register(ctx):
    await ctx.message.delete()

    if '%s' % ctx.author in db.keys():

        current_mmr = db['%s' % ctx.author]
        current_rank = calculate_rank(current_mmr)

        # reset embed
        reset_embed = discord.Embed(
            title=
            "You are already registered. Would you like to update your rank?",
            description="React to answer")
        reset_embed.add_field(name="Current Rank", value=current_rank)
        reset_embed.set_footer(text=str(ctx.author))

        reset_message = await ctx.send(embed=reset_embed)
        await reset_message.add_reaction("✅")
        await reset_message.add_reaction("❌")
        reset_emoji = ["✅", "❌"]

        try:
            reaction, member = await bot.wait_for(
                "reaction_add",
                check=lambda reaction, user: reaction.message.channel == ctx.
                channel and user != bot.user and str(reaction.emoji
                                                     ) in reset_emoji)

            if reaction:
                await reset_message.delete()
                reset_confirm = str(reaction.emoji)
                if reset_confirm == reset_emoji[0]:
                    # update
                    print("New update")
                elif reset_confirm == reset_emoji[1]:
                    clear()
                    return
        except asyncio.TimeoutError:
            await reset_message.delete()

  # check that the user is the one that is replying
    def check(m):
      return m.author == ctx.author and m.channel == ctx.channel

    # asking for username
    usernameEmbed = discord.Embed(
        title="Please enter your name",
        description="This will timeout after 1 minute")
    usernameEmbed.set_footer(text=str(ctx.author))

    # asking for rank
    rankEmbed = discord.Embed(title="Please enter your rank",
                              color=discord.Color.red())
    rankEmbed.add_field(
        name="Ranks",
        value=
        "Radiant\nImmortal\nDiamond\nPlatinum\nGold\nSilver\nBronze\nIron",
        inline=True)
    rankEmbed.set_footer(text=str(ctx.author))

    # asking for division
    divisionEmbed = discord.Embed(title="Please enter your division",
                                  color=discord.Color.red())
    divisionEmbed.add_field(name="Divisions", value="1, 2, 3", inline=True)
    divisionEmbed.set_footer(text=str(ctx.author))

    # asking for rr
    rrEmbed = discord.Embed(title="Please enter your RR",
                            description="An estimate works")
    rrEmbed.set_footer(text=str(ctx.author))

    # confirmation
    confirmation_embed = discord.Embed(title=str(ctx.author) +
                                 " has been registered.",
                                 description="Type ?join to join the queue")

    # Username Embed
    # using the discord name as username
    # username = str(ctx.author)
    username = ctx.author

    # # using input as username
    # sentUsername = await ctx.send(embed=usernameEmbed)
    # try:
    #     msg = await bot.wait_for(
    #         "message",
    #         timeout=60,
    #         # check=lambda message:message.author == ctx.author and message.channel == ctx.channel
    #         check=check)
    #     if msg:
    #         await sentUsername.delete()
    #         await msg.delete()
    #         username = msg.content
    # except asyncio.TimeoutError:
    #     await sentUsername.delete()
    #     await ctx.send("Cancelling due to timeout", delete_after=10)
    #     return


    # Rank Embed
    sentRanks = await ctx.send(embed=rankEmbed)
    try:
        msg = await bot.wait_for(
            "message",
            timeout=60,
            # check=lambda message:message.author == ctx.author and message.channel == ctx.channel
            check=check)
        if msg:
            await sentRanks.delete()
            await msg.delete()
            rank = msg.content.lower()
            # await ctx.send(msg.content) # this is sending it back
    except asyncio.TimeoutError:
        await sentRanks.delete()
        await ctx.send("Cancelling due to timeout", delete_after=10)

    # print("this is rank" + str(rank))


    # Division Embed
    if (rank == "immortal" or rank == "radiant"):
        division = 1
    else:
        sentDivision = await ctx.send(embed=divisionEmbed)
        try:
            msg = await bot.wait_for(
                "message",
                timeout=60,
                # check=lambda message:message.author == ctx.author and message.channel == ctx.channel
                check=check)
            if msg:
                await sentDivision.delete()
                await msg.delete()
                division = msg.content
                if int(division) > 3 or int(division) == 0:
                    await ctx.send("Please enter a valid division",
                                    delete_after=10)
                    return
                # await ctx.send(msg.content) # this is sending it back
        except asyncio.TimeoutError:
            await sentDivision.delete()
            await ctx.send("Cancelling due to timeout", delete_after=10)

    # RR Embed
    sentRR = await ctx.send(embed=rrEmbed)
    try:
        msg = await bot.wait_for(
            "message",
            timeout=60,
            # check=lambda message:message.author == ctx.author and message.channel == ctx.channel
            check=check)
        if msg:
            await sentRR.delete()
            await msg.delete()
            rr = msg.content
            # await ctx.send(msg.content) # this is sending it back
    except asyncio.TimeoutError:
        await sentRR.delete()
        await ctx.send("Cancelling due to timeout", delete_after=10)

    mmr = calculate_mmr(rank, division, rr)
    db[username] = mmr

    await ctx.send(embed=confirmation_embed, delete_after=10)


@bot.command()
async def join(ctx):
    global queue
    await ctx.message.delete()

    # check that the user is the one that is replying
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    # confirmation
    joined_embed = discord.Embed(title=str(ctx.author) +
                                 " has joined the queue.",
                                 description="Type ?start to start the game")

    # confirmation
    not_registered_embed = discord.Embed(title=str(ctx.author) +
                                 " is not registered.",
                                 description="Type ?register to register your rank")
    # queue
    queue_embed = discord.Embed(
        title="Queue", description="Current players that are in queue: ")

    # queue amt check
    noStartEmbed = discord.Embed(title="Too many players")
    if len(players) >= 10:
        await ctx.send(embed=noStartEmbed, delete_after=10)
        return

    if '%s' % ctx.author in db.keys():
      mmr = db['%s' % ctx.author]
    else:
      await ctx.send(embed=not_registered_embed, delete_after=10)
      return

    # using the discord name as username
    username = ctx.author

    # check if already in
    for member in players:
        if member.user == username:
            await ctx.send("You have already joined the queue",
                           delete_after=10)
            return

    # create player
    new_player = Player(username, mmr)
    players.append(new_player)
        
    # update queue
    queue_names = []
    for player in players:
        queue_names.append(str(player.user))
    queue_embed.add_field(name="Players", value=queue_names, inline=True)

    # ctx.message.delete()
    await ctx.send(embed=joined_embed, delete_after=10)
    # queue = await ctx.send(embed=queue_embed, delete_after=120)


@bot.command()
async def queue(ctx):
    await ctx.message.delete()
    global queue
    queue_names = []
    # queue
    queue_embed = discord.Embed(
        title="Queue", description="Current players that are in queue: ")

    no_queue_embed = discord.Embed(
        title="No one in queue",
        description="Please use ?join to join the queue")

    if len(players) == 0:
        await ctx.send(embed=no_queue_embed, delete_after=10)
        return

    for player in players:
        queue_names.append(str(player.user))

    queue_string = list_to_string(queue_names)
    queue_embed.add_field(name="Players", value=queue_string, inline=True)
    players_string = str(len(players)) + " in queue"
    queue_embed.set_footer(text=players_string)

    await ctx.send(embed=queue_embed, delete_after=30)

    # if queue == None:
    #   queue = await ctx.send(embed=queue_embed, delete_after=60)
    # else:
    #   queue.delete()
    #   queue = await ctx.send(embed=queue_embed, delete_after=60)


@bot.command()
async def unjoin(ctx):
    await ctx.message.delete()
    global queue, players
    unjoin_user = str(ctx.author)

    unjoined_embed = discord.Embed(
        title=str(ctx.author) + " has successfully left the queue",
        description="Please use ?queue to see the queue")

    no_queue_embed = discord.Embed(
        title="No one in queue",
        description="Please use ?join to join the queue")

    if len(players) == 0:
        await ctx.send(embed=no_queue_embed, delete_after=10)
        return

    for player in players:
        if str(player.user) == unjoin_user:
            players.remove(player)

    await ctx.send(embed=unjoined_embed, delete_after=10)


@bot.command()
async def unmove(ctx):
    await ctx.message.delete()

    # move channel embed
    move_embed = discord.Embed(
        title="Would you like to move players back?",
        description="React to have members move to channel")

    move_message = await ctx.send(embed=move_embed)
    await move_message.add_reaction("✅")
    await move_message.add_reaction("❌")
    move_emoji = ["✅", "❌"]

    absolute_channel = bot.get_channel(597613500163948580)

    try:
        reaction, member = await bot.wait_for(
            "reaction_add",
            check=lambda reaction, user: reaction.message.channel == ctx.
            channel and user != bot.user and str(reaction.emoji) in move_emoji)

        if reaction:
            await move_message.delete()
            move_confirm = str(reaction.emoji)
            if move_confirm == move_emoji[0]:
                # move channel
                for player in team1list:
                    await player.user.move_to(absolute_channel)
                for player in team2list:
                    await player.user.move_to(absolute_channel)

            elif move_confirm == move_emoji[1]:
                clear()
                # await ctx.send("Invalid", delete_after=10)
                #await bot.move_member(member, team1_channel)

                # for member in players:
                #   # member_move = bot.get_member(member.user_id)
                #   # await member_move.move_to(team1_channel)

                #   await bot.move_member(member.user, team1_channel)

                # for member in team1:
                #     member_move = bot.get_member(member.user_id)
                #     await member_move.move_to(team1_channel)

                # for member in team2:
                #     member_move = bot.get_member(member.user_id)
                #     await member_move.move_to(team2_channel)
    except asyncio.TimeoutError:
        await move_message.delete()


@bot.command()
async def move(ctx):
    await ctx.message.delete()
    # move channel embed
    move_embed = discord.Embed(
        title="Would you like to move the teams to their channels?",
        description="React to have members move to channel")

    move_message = await ctx.send(embed=move_embed)
    await move_message.add_reaction("✅")
    await move_message.add_reaction("❌")
    move_emoji = ["✅", "❌"]

    try:
        reaction, member = await bot.wait_for(
            "reaction_add",
            check=lambda reaction, user: reaction.message.channel == ctx.
            channel and user != bot.user and str(reaction.emoji) in move_emoji)

        if reaction:
            await move_message.delete()
            move_confirm = str(reaction.emoji)
            if move_confirm == move_emoji[0]:
                # move channel
                team1_channel = bot.get_channel(856340072299233340)
                team2_channel = bot.get_channel(856340109418561546)

                for member in team1list:
                    await member.user.move_to(team1_channel)

                for member in team2list:
                    await member.user.move_to(team2_channel)

            elif move_confirm == move_emoji[1]:
                clear()
                # await ctx.send("Invalid", delete_after=10)
                #await bot.move_member(member, team1_channel)

                # for member in players:
                #   # member_move = bot.get_member(member.user_id)
                #   # await member_move.move_to(team1_channel)

                #   await bot.move_member(member.user, team1_channel)

                # for member in team1:
                #     member_move = bot.get_member(member.user_id)
                #     await member_move.move_to(team1_channel)

                # for member in team2:
                #     member_move = bot.get_member(member.user_id)
                #     await member_move.move_to(team2_channel)
    except asyncio.TimeoutError:
        await move_message.delete()
        # await ctx.send("Invalid", delete_after=10)


@bot.command()
async def test(ctx):
    await ctx.message.delete()
    global players
    players = example_players
    await ctx.send("Test Players Loaded", delete_after=10)


@bot.command()
async def start(ctx):
    await ctx.message.delete()
    repeat = True

    while repeat:
        repeat = False
        not_enough_embed = discord.Embed(
            title="Not enough players",
            description=("There are only " + str(len(players)) +
                         " players joined."))

        if len(players) < 10:
            await ctx.send(embed=not_enough_embed, delete_after=10)
        else:
            team1list, team2list, diff = calculate_teams(players)

            # testing
            win_perc(team1list, team2list)

            selected_map = str(pick_map())

            # match embed
            match_embed = discord.Embed(title=selected_map,
                                        color=discord.Color.red())
            match_embed.add_field(name="Team 1",
                                  value=team_to_list(team1list),
                                  inline=True)
            match_embed.add_field(name="Team 2",
                                  value=team_to_list(team2list),
                                  inline=True)
            match_embed.set_footer(text=pick_side())
            match_embed.set_image(url=map_image(selected_map))
            game_info_embed = await ctx.send(embed=match_embed)
            refresh_emoji = "🔄"
            await game_info_embed.add_reaction(refresh_emoji)

            #refresh map
            await ctx.send(
                "You may react to change map and sides (10 seconds)",
                delete_after=10)

            try:
                reaction, member = await bot.wait_for(
                    "reaction_add",
                    check=lambda reaction, user: reaction.message.channel ==
                    ctx.channel and user != bot.user and str(
                        reaction.emoji) == refresh_emoji,
                    timeout=10)

                if reaction:
                    await game_info_embed.delete()
                    repeat = True
                    continue
            except asyncio.TimeoutError:
                await game_info_embed.clear_reactions()
                # await refresh_info.delete()
                # return

            # results
            # result embed
            winner_embed = discord.Embed(title="Who was the winner?",
                                         description="Team 1 or Team 2")

            score_embed = discord.Embed(title="What was the score?",
                                        description="Example: 13-9")

            # play again embed
            again_embed = discord.Embed(
                title="Would you like to play again?",
                description="Restart the game with the same players")

            # move channel embed
            move_embed = discord.Embed(
                title="Would you like to move the teams to their channels?",
                description="React to have members move to channel")

            move_message = await ctx.send(embed=move_embed)
            await move_message.add_reaction("✅")
            await move_message.add_reaction("❌")
            move_emoji = ["✅", "❌"]
            try:
                reaction, member = await bot.wait_for(
                    "reaction_add",
                    check=lambda reaction, user: reaction.message.channel ==
                    ctx.channel and user != bot.user and str(reaction.emoji
                                                             ) in move_emoji)

                if reaction:
                    await move_message.delete()
                    move_confirm = str(reaction.emoji)
                    if move_confirm == move_emoji[0]:
                        # move channel
                        team1_channel = bot.get_channel(856340072299233340)
                        team2_channel = bot.get_channel(856340109418561546)

                        for member in team1list:
                            await member.user.move_to(team1_channel)

                        for member in team2list:
                            await member.user.move_to(team2_channel)

                    elif move_confirm == move_emoji[1]:
                        clear()
            except asyncio.TimeoutError:
                await move_message.delete()
                # await ctx.send("Invalid", delete_after=10)

            # asking about who was winner
            await asyncio.sleep(10)
            sent_winner = await ctx.send(embed=winner_embed)
            await sent_winner.add_reaction("1️⃣")
            await sent_winner.add_reaction("2️⃣")

            team_emoji = ["1️⃣", "2️⃣"]

            try:
                reaction, member = await bot.wait_for(
                    "reaction_add",
                    check=lambda reaction, user: reaction.message.channel ==
                    ctx.channel and user != bot.user and str(reaction.emoji
                                                             ) in team_emoji)
            except asyncio.TimeoutError:
                await sent_winner.delete()
                await ctx.send("Invalid", delete_after=10)
                # return

            if str(reaction.emoji) == team_emoji[0]:
                await sent_winner.delete()
                # await msg.delete()
                winner = "Team 1"
            elif (reaction.emoji) == team_emoji[1]:
                await sent_winner.delete()
                # await msg.delete()
                winner = "Team 2"

            # asking about who was winner
            sent_score = await ctx.send(embed=score_embed)
            try:
                msg = await bot.wait_for(
                    "message",
                    timeout=60,
                    # check=lambda message:message.author == ctx.author and message.channel == ctx.channel
                )
                if msg:
                    await sent_score.delete()
                    await msg.delete()
                    score = str(msg.content)
            except asyncio.TimeoutError:
                await sent_score.delete()
                await ctx.send("Cancelling due to timeout", delete_after=10)
                return

            match_embed.add_field(name="Result",
                                  value="The winner was " + winner +
                                  " with a score of " + score,
                                  inline=False)

            match_history_channel = bot.get_channel(856067674354352131)
            await match_history_channel.send(embed=match_embed)
            await game_info_embed.delete()

            again_message = await ctx.send(embed=again_embed)
            await again_message.add_reaction("✅")
            await again_message.add_reaction("❌")

            again_emoji = ["✅", "❌"]
            try:
                reaction, member = await bot.wait_for(
                    "reaction_add",
                    check=lambda reaction, user: reaction.message.channel ==
                    ctx.channel and user != bot.user and str(reaction.emoji
                                                             ) in again_emoji)

                if reaction:
                    await again_message.delete()
                    again_confirm = str(reaction.emoji)
                    if again_confirm == again_emoji[0]:
                        repeat = True
                    elif again_confirm == again_emoji[1]:
                        clear()
            except asyncio.TimeoutError:
                await again_message.delete()
                await ctx.send("Invalid", delete_after=10)
                return

            unmove(ctx)

# run the bot
# keep_alive()
bot.run(TOKEN)
