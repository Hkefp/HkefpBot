import os
from discord import Embed
from ossapi import OssapiAsync, GameMode, Mod
from discord.ext import commands
import requests

def simple_embed(title: str, description: str, fields: list = [], footer: str = None , footer_icon: str = None, image: str = None, thumbnail: str = None, author_name: str = None,
    author_icon: str = None, author_url: str = None) -> Embed:
    embed = Embed(title=title, description=description)
    # fields is a list of name/value pair tuples
    for name, value in fields:
        embed.add_field(name=name, value=value, inline=False)

    embed.set_footer(text=footer, icon_url=footer_icon)
    embed.set_author(name=author_name, url=author_url, icon_url=author_icon)
    embed.set_image(url=image)
    embed.set_thumbnail(url=thumbnail)
    return embed

class Osu(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.osu = OssapiAsync(int(os.environ.get("OSU_ID")), os.environ.get("OSU_SECRET"))
        self.beatmap_value = {}
        self.beatmap_mode = {} 

    @commands.command(aliases=["avatar"] + ["av"],  description="Check an users Osu! avatar.")
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def osuavatar(self, context, *, username: str = None):

        register_cog = self.bot.get_cog("User")

        if username:
            target_username = username
        else:
            target_username = register_cog.get_username(context.author.id)
            if not target_username:
                return

        # fetch the user
        user = await self.osu.user(target_username)

        # building the embed
        flag_url = f"https://flagsapi.com/{user.country_code}/flat/64.png"

        # send the embed
        await context.reply(embed=simple_embed(f"", f"", author_name=f"{user.username}", author_url=f"https://osu.ppy.sh/users/{user.id}", author_icon=flag_url, image=f"{user.avatar_url}"), mention_author=False)

# OSU PROFILES @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    @commands.command(aliases=['osu'] + ["taiko"] + ["catch"] + ["ctb"] + ["mania"],  description="Check the statistics of an osu! profile.")
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def osustats(self, context, *, username: str = None):
        
        # check what aliases the user used
        invoked = context.invoked_with.lower()
        if invoked.startswith("taiko"):   
            gamemode = GameMode.TAIKO
            gamemode_icon = 1
        elif invoked.startswith("catch") or invoked.startswith("ctb"):   
            gamemode = GameMode.CATCH
            gamemode_icon = 2
        elif invoked.startswith("mania"):   
            gamemode = GameMode.MANIA
            gamemode_icon = 3
        else:
            gamemode = GameMode.OSU
            gamemode_icon = 0

        # username data
        register_cog = self.bot.get_cog("User")
        if username:
            target_username = username
        else:
            target_username = register_cog.get_username(context.author.id)
            if not target_username:
                return
            
        # fetch the users data
        user = await self.osu.user(target_username, mode=gamemode)

        # in case the users country is non existent or something like that..
        flag = user.country_code or "XX"
        if flag == "XX":
            flag_url = "https://emojiapi.dev/api/v1/red_question_mark/64.png"
        else:
            flag_url = f"https://flagsapi.com/{user.country_code}/flat/64.png"

        gamemode_icon = os.environ.get(f"{gamemode_icon}")
        
        # building the embed
        if getattr(user.statistics.level, "progress") < 9:
            max_level = f"0{getattr(user.statistics.level, "progress")}"
        else:
            max_level = f"{getattr(user.statistics.level, "progress")}"

        grade_counts_ssh = getattr(user.statistics.grade_counts, "ssh")
        grade_counts_ss = getattr(user.statistics.grade_counts, "ss")
        grade_counts_s = getattr(user.statistics.grade_counts, "s")
        grade_counts_sh = getattr(user.statistics.grade_counts, "sh")
        grade_counts_a = getattr(user.statistics.grade_counts, "a")

        field_ranks = (f"Total Grades", f"{os.environ.get(f"SSH")}{grade_counts_ssh or 0:,}{os.environ.get(f"SS")}{grade_counts_ss or 0:,}{os.environ.get(f"SH")}{grade_counts_sh or 0:,}{os.environ.get(f"S")}{grade_counts_s or 0:,}{os.environ.get(f"A")}{grade_counts_a or 0:,}")
        # send the embed
        await context.reply(embed=simple_embed(f"{user.title or ""}", f"\nRanked score: {user.statistics.ranked_score or 0:,}\nAccuracy: {user.statistics.hit_accuracy or 0:.2f}% Lvl: {getattr(user.statistics.level, "current")}.{max_level}\nPlaycount: {user.statistics.play_count or 0:,} ({round(user.statistics.play_time / 3600):,} Hrs)\nReplays watched: {user.statistics.replays_watched_by_others or 0:,}", fields=[field_ranks], thumbnail=user.avatar_url, footer=f"Joined {user.join_date.strftime("%B %d, %Y")}", author_name=f"{user.username}: {round(user.statistics.pp or 0):,}pp (#{user.statistics.global_rank or 0:,}) {user.country_code or "??"}#{user.statistics.country_rank or 0}", author_url=f"https://osu.ppy.sh/users/{user.id}", footer_icon=gamemode_icon, author_icon=flag_url), mention_author=False)

# RECENT PLAY @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    @commands.command(aliases=["r"] + [f"r{i}" for i in range(1, 100)] + ["rt"] + [f"rt{i}" for i in range(1, 100)] + ["rc"] + [f"rc{i}" for i in range(1, 100)] + ["rm"] + [f"rm{i}" for i in range(1, 100)],  description="recent play")
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def recent(self, context, *, username: str = None):

        # check what aliases the user used
        invoked = context.invoked_with.lower()
        if invoked.startswith("rt"):   
            gamemode = GameMode.TAIKO
            idx_part = invoked[2:]
        elif invoked.startswith("rc"):
            gamemode = GameMode.CATCH
            idx_part = invoked[2:]
        elif invoked.startswith("rm"):
            gamemode = GameMode.MANIA
            idx_part = invoked[2:]
        else:                          
            gamemode = GameMode.OSU
            idx_part = invoked[1:]

        # select the index the user put next to the comand
        index = int(idx_part) if idx_part.isdigit() else 1

        # username data
        register_cog = self.bot.get_cog("User")
        if username:
            target_username = username
        else:
            target_username = register_cog.get_username(context.author.id)
            if not target_username:
                return
            
        # fetch the user and recent scores
        user = await self.osu.user(target_username, mode=gamemode)
        recent_scores = await self.osu.user_scores(user.id, "recent", mode=gamemode, legacy_only=True, include_fails=False, limit=index)

        if not recent_scores: 
            return await context.reply(f"The user **{user.username}** has no recent score in this gamemode.", mention_author=False)
    
        try:
            recent = recent_scores[index - 1]
        except IndexError:
            return await context.send(f"The user **{target_username.capitalize()}** has no recent play #{index}.")


        # if the score is in the top 50 of the map
        rank_on_map = ""
        if recent.has_replay:

            leaderboard_obj = await self.osu.beatmap_scores(recent.beatmap_id, mode=gamemode, limit=50, legacy_only=True)
            leaderboard = leaderboard_obj.scores
            for i, score in enumerate(leaderboard, start=1):
                if score.user_id == user.id and score.legacy_total_score == recent.legacy_total_score:
                    rank_on_map = f"**__Global Top #{i}__**"
                    break

        # mods for difficulty calculation
        mods = recent_scores[0].mods
        mod_acronyms = [mod.acronym.replace("CL", "") for mod in mods]
        mod_acronyms.sort(key=lambda x: 0 if x == "DT" else 1) # THIS WILL PRIORITIZE THE DT MOD SO IT GOES FIRST SO THINGS LIKE DTHD WORK AS HDDT BECAUSE FOR SOME REASON IT JUST DOESNT WORK WHEN USING MULTIPLE MODS
        mod_objects = [getattr(Mod, m) for m in mod_acronyms if hasattr(Mod, m)]

        stars = await self.osu.beatmap_attributes(recent.beatmap.id, mods=mod_objects)

        if recent.mods:
            mod_list = [mod.acronym for mod in recent.mods if mod.acronym != "CL"]
            mod_str_embed = "".join(mod_list) if mod_list else "NM"
        else:
            mod_str_embed = "NM"
        
        # mods for bpm calculation
        bpm = recent.beatmap.bpm
        if any(mod.acronym == "DT" for mod in mods):
            bpm *= 1.5
        elif any(mod.acronym == "HT" for mod in mods):
            bpm *= 0.75
        bpm = round(bpm, 1)
        bpm_display = int(bpm) if bpm.is_integer() else bpm

        # building the embed
        flag_url = f"https://flagsapi.com/{user.country_code}/flat/64.png"

        times_stamp = int(recent.ended_at.timestamp())
        time_embed = f"<t:{times_stamp}:R>"
        
        emoji_rank = os.environ.get(f"{recent.rank.name}")
        gamemode_icon = os.environ.get(f"{recent.beatmap.mode_int}")
        beatmap_full = await self.osu.beatmap(recent.beatmap.id)
        field_info = f"{emoji_rank}+ {mod_str_embed} • {recent.accuracy * 100:.2f}% • {round(recent.pp or 0)}pp • {recent.max_combo}x/{beatmap_full.max_combo}x • {recent.statistics.miss or 0}<:hit0:1422978270130868285>\nScore: {recent.legacy_total_score:,} • {bpm_display} BPM  {time_embed}"
        
        # send the embed
        await context.reply(embed=simple_embed(f"", f"### [{recent.beatmapset.title} [{recent.beatmap.version}] ({stars.attributes.star_rating:.2f}★)]({recent.beatmap.url})\n{rank_on_map}\n{field_info}", footer=f"{recent.beatmapset.status.name[0].upper()+recent.beatmapset.status.name[1:].lower()} mapset made by {recent.beatmapset.creator}", footer_icon=gamemode_icon, author_name=f"{user.username} (#{user.statistics.global_rank:,}) {user.country_code}#{user.statistics.country_rank:,}", author_icon=flag_url, author_url=f"https://osu.ppy.sh/users/{user.id}"),  mention_author=False)
        
        # store data for the "compare" command
        self.beatmap_value = recent.beatmap.id
        self.beatmapset_value = recent.beatmap.beatmapset_id
        self.beatmap_mode = gamemode

# TOP PLAYS @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    @commands.command(aliases=['top'] + [f"top{i}" for i in range(1, 100)] + ['topt'] + [f"topt{i}" for i in range(1, 100)] + ['topc'] + [f"topc{i}" for i in range(1, 100)] + ['topm'] + [f"topm{i}" for i in range(1, 100)],  description="TOP PLAYS")
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def top_plays(self, context, *, username: str = None):

        # check what aliases the user used
        invoked = context.invoked_with.lower()
        if invoked.startswith("topt"):   
            gamemode = GameMode.TAIKO
            idx_part = invoked[4:]
            mode_int = 1
        elif invoked.startswith("topc"):
            gamemode = GameMode.CATCH
            idx_part = invoked[4:]
            mode_int = 2
        elif invoked.startswith("topm"):
            gamemode = GameMode.MANIA
            idx_part = invoked[4:]
            mode_int = 3
        else:                          
            gamemode = GameMode.OSU
            idx_part = invoked[3:]
            mode_int = 0

        # select the index the user put next to the comand
        index = int(idx_part) if idx_part.isdigit() else 10

        # username data
        register_cog = self.bot.get_cog("User")
        if username:
            target_username = username
        else:
            target_username = register_cog.get_username(context.author.id)
            if not target_username:
                return
        
        # fetch user and scores
        user = await self.osu.user(target_username, mode=gamemode)
        scores = await self.osu.user_scores(user.id, "best", mode=gamemode, legacy_only=True, limit=index)
        
        if not scores:
            return await context.reply("This user has no top plays.")

        # if the user selected an index to view
        if idx_part:
            try:
                score = scores[index - 1]
            except IndexError:
                return await context.reply(f"{user.username} has no top play #{index}.")
        
            bm = score.beatmap
            bms = score.beatmapset
            mods = score.mods
            
            url = None

            mod_acronyms = [mod.acronym.replace("CL", "") for mod in mods]
            mod_acronyms.sort(key=lambda x: 0 if x == "DT" else 1) # THIS WILL PRIORITIZE THE DT MOD SO IT GOES FIRST SO THINGS LIKE DTHD WORK AS HDDT BECAUSE FOR SOME REASON IT JUST DOESNT WORK WHEN USING MULTIPLE MODS
            mod_objects = [getattr(Mod, m) for m in mod_acronyms if hasattr(Mod, m)]

            stars = await self.osu.beatmap_attributes(score.beatmap_id, mods=mod_objects)

            if score.mods:
                mod_list = [mod.acronym for mod in score.mods if mod.acronym != "CL"]
                mod_str_embed = "".join(mod_list) if mod_list else "NM"
            else:
                mod_str_embed = "NM"

            bpm = bm.bpm
            if any(mod.acronym == "DT" for mod in mods):
                bpm *= 1.5
            elif any(mod.acronym == "HT" for mod in mods):
                bpm *= 0.75
            bpm = round(bpm, 1)
            bpm_display = int(bpm) if bpm.is_integer() else bpm

            flag_url = f"https://flagsapi.com/{user.country_code}/flat/64.png"
            
            # miss count
            if score.statistics.miss:
                miss = f" • {score.statistics.miss}<:hit0:1422978270130868285>"
            if not score.statistics.miss:
                miss = ""

            # building the embed
            scoreendvalue = int(score.ended_at.timestamp())
            scoreend = f"<t:{scoreendvalue}:R>"
            title_display = bms.title if len(bms.title) <= 60 else bms.title[:40] + "..."
            emoji_rank = os.environ.get(f"{score.rank.name}")
            field_scores = []
            description = f"### [{score.beatmapset.title} [{score.beatmap.version}] ({stars.attributes.star_rating:.2f}★)]({score.beatmap.url})\n**__Personal Best #{index}__**\n{emoji_rank}+ {mod_str_embed} • {score.accuracy * 100:.2f}% • {round(score.pp or 0)}pp • {score.max_combo}x • {score.statistics.miss or 0}<:hit0:1422978270130868285>\nScore: {score.legacy_total_score:,} • {bpm_display} BPM  {scoreend}"
            gamemode_icon = os.environ.get(f"{score.beatmap.mode_int}")
            footer_text = f"{score.beatmapset.status.name[0].upper()+score.beatmapset.status.name[1:].lower()} mapset made by {score.beatmapset.creator}"
            
            # store beatmap data for the command "compare"
            self.beatmap_value = score.beatmap.id
            self.beatmapset_value = score.beatmap.beatmapset_id
            if score.beatmap.mode.value.upper() == "FRUITS":
                self.beatmap_mode = GameMode["CATCH"]
            else:
                self.beatmap_mode = GameMode[score.beatmap.mode.value.upper()]

            # if the user did not enter an index to view
        else:

            description = ""
            field_scores = []
            footer_text = f"1/1  •  Showing current top 10 plays by {user.username.capitalize()}"
            gamemode_icon = os.environ.get(f"{mode_int}")
            url = user.avatar_url

            # loop the best plays
            for i, score in enumerate(scores, start=1):
                bm = score.beatmap
                bms = score.beatmapset
                mods = score.mods

                mod_acronyms = [mod.acronym.replace("CL", "") for mod in mods]
                mod_acronyms.sort(key=lambda x: 0 if x == "DT" else 1) # THIS WILL PRIORITIZE THE DT MOD SO IT GOES FIRST SO THINGS LIKE DTHD WORK AS HDDT BECAUSE FOR SOME REASON IT JUST DOESNT WORK WHEN USING MULTIPLE MODS
                mod_objects = [getattr(Mod, m) for m in mod_acronyms if hasattr(Mod, m)]

                stars = await self.osu.beatmap_attributes(score.beatmap_id, mods=mod_objects)

                if score.mods:
                    mod_list = [mod.acronym for mod in score.mods if mod.acronym != "CL"]
                    mod_str_embed = "".join(mod_list) if mod_list else "NM"
                else:
                    mod_str_embed = "NM"

                bpm = bm.bpm
                if any(mod.acronym == "DT" for mod in mods):
                    bpm *= 1.5
                elif any(mod.acronym == "HT" for mod in mods):
                    bpm *= 0.75
                bpm = round(bpm, 1)
                bpm_display = int(bpm) if bpm.is_integer() else bpm

                flag_url = f"https://flagsapi.com/{user.country_code}/flat/64.png"
                
                # miss count
                if score.statistics.miss:
                    miss = f" • {score.statistics.miss}<:hit0:1422978270130868285>"
                if not score.statistics.miss:
                    miss = ""

                # build the embed
                scoreendvalue = int(score.ended_at.timestamp())
                scoreend = f"<t:{scoreendvalue}:R>"
                title_display = bms.title if len(bms.title) <= 60 else bms.title[:40] + "..."
                emoji_rank = os.environ.get(f"{score.rank.name}")
                field_scores.append((f"#{i} {title_display} [{bm.version}] {stars.attributes.star_rating:.2f}★", f"{emoji_rank}+ {mod_str_embed} • {score.accuracy * 100:.2f}% • {round(score.pp or 0)}pp {scoreend} {bpm_display} BPM{miss}"))

        # send the embed
        await context.reply(embed=simple_embed(f"", description=description, fields=field_scores, thumbnail=url, author_name=f"{user.username} (#{user.statistics.global_rank:,}) {user.country_code}#{user.statistics.country_rank:,}", author_url=f"https://osu.ppy.sh/users/{user.id}", author_icon=flag_url, footer_icon=gamemode_icon, footer=footer_text),  mention_author=False)

# CHECK MAP @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@    
    @commands.command(aliases=['map'] + ['m'],  description="check a map")
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def get_map(self, context, *, map_id: int = None):
        
        # check if the user sent the id of the map or not..
        if map_id is None:
            map_id = self.beatmap_value
        
        # fetch beatmap and beatmapset
        beatmap = await self.osu.beatmap(map_id)
        beatmapset = await self.osu.beatmapset(beatmap.beatmapset_id)

        # building the embed
        bpm_display = int(beatmap.bpm) if beatmap.bpm.is_integer() else beatmap.bpm
        beatmap_length = f"{beatmap.total_length // 60}:{beatmap.total_length % 60:02}"
        beatmap_status = beatmapset.status.name[0].upper()+beatmapset.status.name[1:].lower()
        beatmap_stats = f"`CS: {beatmap.cs} HP: {beatmap.drain} OD: {beatmap.accuracy} AR: {beatmap.ar}`"

        bg = f"{beatmapset.covers.cover_2x}" 
        beatmap_mode = os.environ.get(f"{beatmap.mode_int}")
        nsfw = ""
        if beatmapset.nsfw:
            nsfw = "🔞"

        field_stats = (f"**__{beatmap.version}__** ({beatmap.difficulty_rating:.2f}★)", f"Circles: {beatmap.count_circles} Sliders: {beatmap.count_sliders} Spinners: {beatmap.count_spinners or "0"}\nMax combo: {beatmap.max_combo}x Length: {beatmap_length} BPM: {bpm_display}\n{beatmap_stats}")
        
        # send the embed
        await context.reply(embed=simple_embed(f"", f"### [{beatmapset.artist} - {beatmapset.title}]({beatmap.url})\n**🌐 {beatmapset.play_count:,} :star: {beatmapset.favourite_count:,} 🏷️ {beatmapset.language["name"]}, {beatmapset.genre["name"]} {nsfw}**", fields=[field_stats], image=bg, author_name="", footer=f"{beatmap_status} mapset made by {beatmapset.creator}", footer_icon=beatmap_mode), mention_author=False)

        # store beatmap data for the command "compare"
        self.beatmap_value = beatmap.id
        self.beatmapset_value = beatmap.beatmapset_id

        if GameMode[beatmap.mode.value.upper()] == "FRUITS":
            self.beatmap_mode = GameMode["CATCH"]
        else:
            self.beatmap_mode = GameMode[beatmap.mode.value.upper()]

# COMPARE @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@QQ
    @commands.command(aliases=["c"] + ["compare"],  description="compare")
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def compareosu(self, context, *, args: str = None):
        
        register_cog = self.bot.get_cog("User")

        # parse args
        map_id = None
        username = None

        if args:
            parts = args.split()
            if parts[0].isdigit():  # first arg must be the map ID
                map_id = int(parts[0])
                username = " ".join(parts[1:]) if len(parts) > 1 else None
            else:
                # if the first arg is not a map ID then use last stored map
                map_id = getattr(self, "beatmap_value", None)
                if not map_id:
                    return await context.reply("No beatmap found.")
                username = " ".join(parts)
        else:
            # if there are no args then use last stored map and registered username
            map_id = getattr(self, "beatmap_value", None)
            if not map_id:
                return await context.reply("No beatmap found.")
            username = None           

        # store the map id for usage if needed
        if map_id:
            self.beatmap_value = map_id

        # get username
        if username:
            target_username = username
        else:
            if not register_cog:
                return
            target_username = register_cog.get_username(context.author.id)
            if not target_username:
                return await context.reply("⚠️ You must register your osu! username first with `!register <username>`.")
           
        # we see if there is a beatmap stored in the global variable
        try:
            beatmap = await self.osu.beatmap(self.beatmap_value)
            beatmapset = await self.osu.beatmapset(beatmap.beatmapset_id)
        except ValueError:
            return await context.send(f"No beatmap was found.")
        
        # fetch gamemode
        if beatmap.mode.value.upper() == "FRUITS":
            gamemode = GameMode["CATCH"]
        else:
            gamemode = GameMode[beatmap.mode.value.upper()]

        try:
            user = await self.osu.user(target_username, mode=gamemode)
        except ValueError:
            return await context.send(f"User **{target_username}** does not exist.")

        # if there are no scores on the map
        try:
            score = await self.osu.beatmap_user_score(beatmap.id, user.id)
        except ValueError:
            return await context.send(f"{user.username.capitalize()} has no scores on this map.")

        # mods for difficulty 
        mods = score.score.mods
        mod_acronyms = [mod.acronym.replace("CL", "") for mod in mods]
        mod_acronyms.sort(key=lambda x: 0 if x == "DT" else 1) # THIS WILL PRIORITIZE THE DT MOD SO IT GOES FIRST SO THINGS LIKE DTHD WORK AS HDDT BECAUSE FOR SOME REASON IT JUST DOESNT WORK WHEN USING MULTIPLE MODS
        mod_objects = [getattr(Mod, m) for m in mod_acronyms if hasattr(Mod, m)]
        
        stars = await self.osu.beatmap_attributes(self.beatmap_value, mods=mod_objects)

        if score.score.mods:
            mod_list = [mod.acronym for mod in score.score.mods if mod.acronym != "CL"]
            mod_str_embed = "".join(mod_list) if mod_list else "NM"
        else:
            mod_str_embed = "NM"
        
        # mods for bpm
        bpm = score.score.beatmap.bpm
        if any(mod.acronym == "DT" for mod in mods):
            bpm *= 1.5
        elif any(mod.acronym == "HT" for mod in mods):
            bpm *= 0.75
        bpm = round(bpm, 1)
        bpm_display = int(bpm) if bpm.is_integer() else bpm

        # building the embed
        times_stamp = int(score.score.ended_at.timestamp())
        time_embed = f"<t:{times_stamp}:R>"
        
        flag = user.country_code or "??"
        if flag == "??":
            flag_url = "https://commons.wikimedia.org/wiki/Category:Flags_with_question_marks#/media/File:Noflag.PNG"
        else:
            flag_url = f"https://flagsapi.com/{user.country_code}/flat/64.png"

        # will change this later, I SWEAR!!!
        if beatmap.mode.name == "OSU":
            footer_url = "https://raw.githubusercontent.com/hiderikzki/osu-difficulty-icons/refs/heads/main/base_std.png"
        if beatmap.mode.name == "TAIKO":
            footer_url = "https://raw.githubusercontent.com/hiderikzki/osu-difficulty-icons/refs/heads/main/base_taiko.png"
        if beatmap.mode.name == "CATCH":
            footer_url = "https://raw.githubusercontent.com/hiderikzki/osu-difficulty-icons/refs/heads/main/base_ctb.png"
        if beatmap.mode.name == "MANIA":
            footer_url = "https://raw.githubusercontent.com/hiderikzki/osu-difficulty-icons/refs/heads/main/base_mania.png"
            return
        
        emoji_rank = os.environ.get(f"{score.score.rank.name}")
        description = f"{emoji_rank}+ {mod_str_embed} • {score.score.accuracy * 100:.2f}% • {round(score.score.pp or 0)}pp • {score.score.max_combo}x/{beatmap.max_combo}x • {score.score.statistics.miss or 0}<:hit0:1422978270130868285>\nScore: {score.score.legacy_total_score:,} • {bpm_display} BPM {time_embed}"
        
        # send the embed
        await context.reply(embed=simple_embed(f"", f"### [{beatmapset.title} [{beatmap.version}] ({stars.attributes.star_rating:.2f}★)]({beatmap.url})\n{description}", footer=f"{beatmapset.status.name[0].upper()+beatmapset.status.name[1:].lower()} mapset made by {beatmapset.creator}", footer_icon=f"{footer_url}", author_name=f"{user.username} (#{user.statistics.global_rank:,}) {user.country_code}#{user.statistics.country_rank:,}", author_url=f"https://osu.ppy.sh/users/{user.id}", author_icon=flag_url),  mention_author=False)
                
        # store beatmap data for the "compare command"
        self.beatmap_value = beatmap.id
        self.beatmapset_value = beatmap.beatmapset_id
        if beatmap.mode.value.upper() == "FRUITS":
            self.beatmap_mode = GameMode["CATCH"]
        else:
            self.beatmap_mode = GameMode[beatmap.mode.value.upper()]

async def setup(bot):
    await bot.add_cog(Osu(bot))