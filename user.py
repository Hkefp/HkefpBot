from discord import Embed
from discord.ext import commands

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

class User(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.usernames = {}
    
    @commands.command(aliases=['helpme'],  description="HELP ME.. HELP.. ME!") # 
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def h(self, context):
        field_osu = ("Osu commands", "osu, taiko, mania, catch, r, rt, rm, rc\nmap, c, top, link, avatar")
        await context.reply(embed=simple_embed(f"", f"### Help!", fields=[field_osu], author_name=""), mention_author=False)

    @commands.command(aliases=['link'],  description="Registers an user")
    @commands.cooldown(1, 3, commands.BucketType.user)
    
    async def registerosu(self, ctx, *, username: str = None):

        # Save username linked to user
        self.usernames[ctx.author.id] = username
        await ctx.send(f"✅ Registered **{username.capitalize()}** as your username.")

    def get_username(self, user_id: int):
        return self.usernames.get(user_id)

async def setup(bot):
    await bot.add_cog(User(bot))