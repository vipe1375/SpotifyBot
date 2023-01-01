import discord 
from discord.ext import commands
from discord import app_commands
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from discord.ui import View
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id='dd9a3e96f45b4ea0bafef437214c135e', client_secret='01396374344d44908ea2bfc2d7fb2484'))

async def setup(bot:commands.Bot):
    await bot.add_cog(Commands(bot))

user_id_glob = None

class ChooseResult(discord.ui.Select):
    def __init__(self, result, type):
        self.result = result
        self.search_type = str(str(type) + 's')
        options = []
        for i in range(len(result[self.search_type]['items'])):
            
            options.append(discord.SelectOption(label=result[self.search_type]['items'][i]['name'], value=i))
        super().__init__(placeholder="Choisissez un résultat",max_values=1,min_values=1,options=options)

    async def callback(self, itr: discord.Interaction):
        if self.search_type == 'artists':
            await self.display_artist(itr, self.result, self.values[0])
        elif self.search_type == 'tracks':
            await self.display_track(itr, self.result, self.values[0])
        elif self.search_type == 'albums':
            await self.display_album(itr, self.result, self.values[0])

    async def display_artist(self, itr: discord.Interaction, result, id):
        
        uri = result['artists']['items'][int(id)]['uri']
        artist = spotify.artist(uri)
        top_tracks = spotify.artist_top_tracks(uri)
        msg = f"""Followers : {artist['followers']['total']}

        __Top titres :__
        > **{top_tracks['tracks'][0]['name']}**
        > **{top_tracks['tracks'][1]['name']}**
        > **{top_tracks['tracks'][2]['name']}**
        """
        embed = discord.Embed(
            title = f"**{artist['name']}**",
            url = artist['external_urls']['spotify'],
            description = msg)
        embed.set_image(url = artist['images'][0]['url'])
        
        await itr.response.edit_message(embed = embed, view=None)

    async def display_album(self, itr: discord.Interaction, result, id):
        uri = result['albums']['items'][int(id)]['uri']
        album = spotify.album(uri)
        msg = f"""Sorti le {album["release_date"]}
        {album['total_tracks']} sons"""
        embed = discord.Embed(title = f"**{album['name']}** par {album['artists'][0]['name']}", description=msg)
        embed.set_image(url = album['images'][0]['url'])
        await itr.response.edit_message(embed = embed, view=None)

    
    async def display_track(self, itr: discord.Interaction, result, id):
        uri = result['tracks']['items'][int(id)]['uri']
        track = spotify.track(uri)
        msg = f"""Album : {track['album']['name']}
        Durée : {int(track['duration_ms']/1000)} secondes
        """
        embed = discord.Embed(title = f"**{track['name']}** par {track['artists'][0]['name']}", description=msg)
        embed.set_image(url = track['album']['images'][0]['url'])
        await itr.response.edit_message(embed = embed, view=None)

    

class Choose(View):
    def __init__(self, result, type, timeout = 0):
        super().__init__()
        self.add_item(ChooseResult(result, type))

class Commands(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    


    # ARTISTS:

    @app_commands.command(
        name='search_artist',
        description="rechercher un artiste")
    async def search_artist(self, itr: discord.Interaction, artist: str):
        result = spotify.search(artist, limit = 10, type='artist')
        msg = ''
        for i in range(len(result['artists']['items'])):
            msg += f"{i+1}.  **{result['artists']['items'][i]['name']}** \n"

        embed = discord.Embed(title=f'Résultats de recherche pour {artist}', description=msg)
        await itr.response.send_message(embed=embed, view=Choose(result, 'artist'))
    
    
    


    # SONGS:

    @app_commands.command(
        name='search_song',
        description="rechercher un son")
    async def search_song(self, itr: discord.Interaction, song: str):
        result = spotify.search(song, limit = 10, type='track')
        
        msg = ''
        for i in range(len(result['tracks']['items'])):
            msg += f"{i+1}.  **{result['tracks']['items'][i]['name']}** - {result['tracks']['items'][i]['artists'][0]['name']} \n"
        embed = discord.Embed(title=f"Résultats de recherche pour {song}", 
                              description=msg)
        await itr.response.send_message(embed=embed, view=Choose(result, 'track'))



    
    # ALBUMS:

    @app_commands.command(
        name = 'search_album',
        description = 'search for an album')
    async def search_album(self, itr: discord.Interaction, album: str):
        result = spotify.search(album, limit = 10, type = 'album')
        msg = ''
        for i in range(len(result['albums']['items'])):
            msg += f"{i+1}.  **{result['albums']['items'][i]['name']}** - {result['albums']['items'][i]['artists'][0]['name']}\n"
        embed = discord.Embed(title = "Résultats de recherche pour " + album, description=msg)
        await itr.response.send_message(embed=embed, view=Choose(result, 'album'))

    


    # PROFILE:

    @app_commands.command(
        name = 'profile',
        description = 'affiche ton profil spotify (si enregistré)')
    async def profile(self, itr: discord.Interaction):
        u_id = user_id_glob
        t = spotify.user(u_id)
        print(t)




    # SAVE:

    @app_commands.command(
        name = "save", 
        description = "sauvegarder votre profil Spotify")
    async def save(self, itr: discord.Interaction, user_url: str):
        user_id = user_url[30:55]
        user = spotify.user(user_id)
        embed = discord.Embed(title = "a")
        embed.set_image(url=user['images'][0]['url'])
        await itr.response.send_message(embed=embed)