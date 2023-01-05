import discord 
from discord.ext import commands
from discord import app_commands
from discord import Interaction
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from discord.ui import View
import spotipy.util as util
import datetime

# Replace CLIENT_ID and CLIENT_SECRET with your own Spotify API credentials
CLIENT_ID = 'bbeddc85beb74252b350314cd2ad5f15'
CLIENT_SECRET = '870d0bfbe0c84eb9bc4e9b2d64efa372'

# Replace USERNAME with your Spotify username
USERNAME = 'Discord'

# Set the scope for the Spotify API. You may need to modify this depending on what you want to do with the API.
SCOPE = 'playlist-read-collaborative playlist-modify-public'

# Set the redirect URI for the Spotify API. You'll need to add this to your Spotify developer dashboard.
REDIRECT_URI = 'http://localhost:8888/callback'

# Set up the Spotify API client
token = util.prompt_for_user_token(USERNAME, SCOPE, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
spotify = spotipy.Spotify(auth=token, client_credentials_manager=SpotifyClientCredentials(
    client_id='bbeddc85beb74252b350314cd2ad5f15', 
    client_secret='870d0bfbe0c84eb9bc4e9b2d64efa372'))


async def setup(bot:commands.Bot):
    await bot.add_cog(Commands(bot))

client = spotify.me()
playlist = spotify.playlist("59ckHwE2dkFjUtjE2wQYzL")
PLAYLIST_ID = "59ckHwE2dkFjUtjE2wQYzL"


votants_pepites = []
sons_pepites_vote = {}
sons_pepites_valides = []

def reload_playlist():
    global playlist
    playlist = spotify.playlist("59ckHwE2dkFjUtjE2wQYzL")

class Choose(View):
    def __init__(self, result, type, user, bot, timeout = 0):
        self.user = user
        super().__init__()
        self.add_item(ChooseResult(result, type, user, bot))

    async def interaction_check(self, itr: Interaction):
        if itr.user != self.user:
            await itr.response.send_message("Ça n'est pas ta commande", ephemeral=True)
        return itr.user == self.user

    async def on_error(self, itr: Interaction, error, item):
        print((error, item))
        await itr.response.send_message((error, item))



class ChooseResult(discord.ui.Select):
    def __init__(self, result, type, user, bot):
        self.user = user
        self.result = result
        self.bot = bot

        self.GUILD_ID = 1052633446595440741
        self.guild = self.bot.get_guild(self.GUILD_ID)

        self.PEPITES_SONS_CHANNEL_ID = 1060556948052914257
        self.pepites_sons_channel = self.bot.get_channel(self.PEPITES_SONS_CHANNEL_ID)
        
        self.search_type = str(str(type) + 's')
        if self.search_type == 'pépites':
            self.search_type = "tracks"
        options = []
        for i in range(len(result[self.search_type]['items'])):
            
            options.append(discord.SelectOption(label=result[self.search_type]['items'][i]['name'], value=i))
        super().__init__(placeholder="Choisissez un résultat",max_values=1,min_values=1,options=options)
        if type == 'pépite':
            self.search_type = 'pépites'

    
    
    async def callback(self, itr: Interaction):
        if self.search_type == 'artists':
            await self.display_artist(itr, self.result, self.values[0])
        elif self.search_type == 'tracks':
            await self.display_track(itr, self.result, self.values[0])
        elif self.search_type == 'albums':
            await self.display_album(itr, self.result, self.values[0])
        elif self.search_type == 'pépites':
            await self.confirm_pepite(itr, self.result, self.values[0])



    async def display_artist(self, itr: Interaction, result, id):
        
        uri = result['artists']['items'][int(id)]['uri']
        artist = spotify.artist(uri)
        top_tracks = spotify.artist_top_tracks(uri)

        # Contenu
        msg = f"""__Followers :__ {artist['followers']['total']}

        __Top titres :__

        """
        for i in range(5):
            track = top_tracks['tracks'][i]

            # plusieurs artistes
            if len(track['artists']) > 1:
                
                # on supprime l'artiste principal de la liste
                for i in range(len(track['artists'])):
                    if track['artists'][i]['id'] == artist['id']:
                        track['artists'].pop(i)
                        break
                
                # on ajoute les autres artistes à la liste des artistes
                e = f"> **{track['name']}** avec "
                for i in range(len(track['artists'])):
                    
                    e += track['artists'][i]['name']
                    if i<len(track['artists'])-1:
                        e += ', '
                    else: 
                        e += "\n"
                msg += e

            # un seul artiste
            else:
                msg += f"> **{track['name']}**\n"

        # Embed
        embed = discord.Embed(
            title = f"**{artist['name']}**",
            url = artist['external_urls']['spotify'],
            description = msg,
            timestamp=datetime.datetime.now())
        embed.set_image(url = artist['images'][0]['url'])
        embed.set_footer(text = itr.user.display_name, icon_url = itr.user.avatar.url)
        await itr.response.edit_message(embed = embed, view=None)



    async def display_album(self, itr: Interaction, result, id):
        uri = result['albums']['items'][int(id)]['uri']
        album = spotify.album(uri)
        
        # Contenu
        artists = ""
        if len(album['artists']) > 1:
            artists = f"s :__ {album['artists'][0]['name']}"
            for i in range(1, len(album['artists'])):
                artists += f", {album['artists'][i]['name']}"
        else:
            artists = f" :__ {album['artists'][0]['name']}"
        
        msg = f"""__Artiste{artists}
        
            __Date de sortie :__ {album["release_date"]}

            __Nombre de pistes :__ {album['total_tracks']}"""

        # Embed
        embed = discord.Embed(title = f"**{album['name']}**",
            description=msg, 
            timestamp=datetime.datetime.now(),
            url = album['external_urls']['spotify'])

        embed.set_image(url = album['images'][0]['url'])
        embed.set_footer(text = itr.user.display_name, icon_url = itr.user.avatar.url)
        await itr.response.edit_message(embed = embed, view=None)




    
    async def display_track(self, itr: Interaction, result, id):
        uri = result['tracks']['items'][int(id)]['uri']
        track = spotify.track(uri)

        # Contenu
        duration = int(track['duration_ms'])/1000
        artists = ""
        if len(track['artists']) > 1:
            artists = f"s :__ {track['artists'][0]['name']}"
            for i in range(1, len(track['artists'])):
                artists += f", {track['artists'][i]['name']}"
        else:
            artists = f" :__ {track['artists'][0]['name']}"

        msg = f"""__Album __: {track['album']['name']}

        __Artiste{artists}

        __Durée :__ {int(duration//60)}:{int(duration%60)}

        __Popularité :__ {track['popularity']}
        """

        # Embed
        embed = discord.Embed(title = f"**{track['name']}** - {track['artists'][0]['name']}",
            description=msg,
            timestamp=datetime.datetime.now(),
            url = track['external_urls']['spotify'])
        embed.set_image(url = track['album']['images'][0]['url'])
        embed.set_footer(text = itr.user.display_name, icon_url = itr.user.avatar.url)
        await itr.response.edit_message(embed = embed, view=None)
        

    async def confirm_pepite(self, itr: Interaction, result, id):
        uri = result['tracks']['items'][int(id)]['uri']
        track = spotify.track(uri)

        if track['id'] in sons_pepites_vote.keys():
            await itr.response.edit_message(content = "Ce son est déjà soumis au vote cette semaine !", embed=None, view=None)
        elif track['id'] in sons_pepites_valides:
            await itr.response.edit_message(content = "Ce son est déjà dans la playlist !", embed=None, view=None)
        else:
            #spotify.playlist_add_items(PLAYLIST_ID, items = [track['id']])
            votants_pepites.append(itr.user.id)
            sons_pepites_vote[track['id']] = 0
            await itr.response.edit_message(content = f"Vous avez proposé **{track['name']}** comme Pépite !", embed=None, view=None)
            await self.pepites_sons_channel.send(f"**{track['name']}**")
        reload_playlist()



class Commands(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
       
    

    @app_commands.command(
        name = 'help',
        description = "commande d'aide du bot")
    async def help(self, itr: Interaction):
        msg = """**COMMANDES**
        
        > `search_artist` -> permet d'afficher des informations sur l'artiste recherché
        > `search_song` -> permet d'afficher des informations sur la chanson recherchée
        > `search_album`-> permet d'afficher des informations sur l'album recherché
        """
        embed = discord.Embed(title = "\u200b", description= msg, timestamp=datetime.datetime.now())
        embed.set_footer(text = itr.user.display_name, icon_url = itr.user.avatar.url)
        
        await itr.response.send_message(embed = embed)


        
    # ARTISTS:

    @app_commands.command(
        name='search_artist',
        description="rechercher un artiste")
    async def search_artist(self, itr: Interaction, artist: str):
        result = spotify.search(artist, limit = 10, type='artist')
        msg = ''
        for i in range(len(result['artists']['items'])):
            msg += f"{i+1}.  **{result['artists']['items'][i]['name']}** \n"

        embed = discord.Embed(title=f'Résultats de recherche pour {artist}', description=msg)
        await itr.response.send_message(embed=embed, view=Choose(result, 'artist', itr.user, self.bot))
    
    
    


    # SONGS:

    @app_commands.command(
        name='search_song',
        description="rechercher un son")
    async def search_song(self, itr: Interaction, song: str):
        result = spotify.search(song, limit = 10, type='track')
        
        msg = ''
        for i in range(len(result['tracks']['items'])):
            msg += f"{i+1}.  **{result['tracks']['items'][i]['name']}** - {result['tracks']['items'][i]['artists'][0]['name']} \n"
        embed = discord.Embed(title=f"Résultats de recherche pour {song}", description=msg)
        await itr.response.send_message(embed=embed, view=Choose(result, 'track', itr.user, self.bot))



    
    # ALBUMS:

    @app_commands.command(
        name = 'search_album',
        description = 'search for an album')
    async def search_album(self, itr: Interaction, album: str):
        result = spotify.search(album, limit = 10, type = 'album')
        msg = ''
        for i in range(len(result['albums']['items'])):
            msg += f"{i+1}.  **{result['albums']['items'][i]['name']}** - {result['albums']['items'][i]['artists'][0]['name']}\n"
        embed = discord.Embed(title = "Résultats de recherche pour " + album, description=msg)
        await itr.response.send_message(embed=embed, view=Choose(result, 'album', itr.user, self.bot))

    


    @app_commands.command(
        name = 'pepite',
        description = 'proposez un son pour la playlist Pépites !')
    async def pepite(self, itr: Interaction, son: str):
        if itr.user.id in votants_pepites:
            await itr.response.send_message("Tu as déjà soumis une pépite cette semaine !", ephemeral=True)
        result = spotify.search(son, limit = 10, type='track')
        msg = ''
        for i in range(len(result['tracks']['items'])):
            msg += f"{i+1}.  **{result['tracks']['items'][i]['name']}** - {result['tracks']['items'][i]['artists'][0]['name']} \n"
        embed = discord.Embed(title=f"Résultats de recherche pour {son}", description=msg)
        await itr.response.send_message(embed=embed, view=Choose(result, 'pépite', itr.user, self.bot))
        


    @app_commands.command(
        name = 'playlist',
        description = 'affiche les informations de la playlist Pépites')
    async def playlist(self, itr: Interaction):
        # Contenu:
        duration = 0
        for i in playlist['tracks']['items']:
            duration += int(i['track']['duration_ms']/1000)
        msg = f"""__Nombre de sons :__ {playlist['tracks']['total']}
        
        __Longueur totale :__ {int(duration//60)}:{int(duration%60)}
        """

        # Embed:
        embed = discord.Embed(
            title = "Pépites", 
            url = playlist['external_urls']['spotify'],
            description = msg,
            timestamp = datetime.datetime.now())
        embed.set_image(url = playlist['images'][0]['url'])
        embed.set_footer(text = itr.user.display_name, icon_url = itr.user.avatar.url)
        await itr.response.send_message(playlist['external_urls']['spotify'], embed = embed)