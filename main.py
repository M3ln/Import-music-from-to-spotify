import spotipy
import vk_api
from vk_api.audio import VkAudio
from spotipy.oauth2 import SpotifyOAuth



def length_dic(tracks_dict):
    res = 0
    for artist in tracks_dict:
        res += len(tracks_dict[artist])
    return res


class ImportFromVKtoSpotify:


    CLIENT_ID = "" # our client id from spotify
    CLIENT_SECRET = "" # our client secret from spotify
    REDIRECT_URI = "http://localhost:8888/callback"
    SCOPE = ["user-library-read", "user-library-modify"]

    def __init__(self, vk_login, vk_password):
        try:
            self.vk_session = vk_api.VkApi(vk_login, vk_password)
            self.vk_session.auth()
            self.vk_audio = VkAudio(self.vk_session)
        except:
            print('Авторизация ВК не пройдена')
            end = input()
        else:
            print('Авторизация ВК пройдена')

        try:
            self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=self.CLIENT_ID,
                                                                client_secret=self.CLIENT_SECRET,
                                                                redirect_uri=self.REDIRECT_URI,
                                                                scope=self.SCOPE))
        except:
            print('Авторизация Spotify не пройдена')
            end = input()
        else:
            print('Авторизация Spotify пройдена')

    def audio_dic_vk(self):
        audio_list = self.vk_audio.get()
        res = dict()
        for audio in audio_list:
            artist = audio['artist'].lower()
            title = audio['title'].lower()
            if artist in list(res.keys()):
                res[artist].append(title)
            else:
                res[artist] = [title]
        return res

    def audio_dic_sp(self):
        tracks = self.sp.current_user_saved_tracks()['items']
        res = dict()
        for audio in tracks:
            if len(audio['track']['artists']) > 1:
                artist_name = ""
                for artist in audio['track']['artists']:
                    artist_name += artist['name']
                    if artist != audio['track']['artists'][-1]:
                        artist_name += ", "
            else:
                artist_name = audio['track']['artists'][0]['name']
            title = audio['track']['name']
            if artist_name in list(res.keys()):
                res[artist_name].append(title)
            else:
                res[artist_name] = [title]
        return res

    def search_in_spoti(self, text):
        res = self.sp.search(text)
        if res['tracks']['items']:
            return res['tracks']['items']
        else:
            return None

    def delete_all_tracks(self):
        tracks_urls = list()
        tracks = self.sp.current_user_saved_tracks()['items']
        for track in tracks:
            tracks_urls.append(track['track']['external_urls']['spotify'])
        self.sp.current_user_saved_tracks_delete(tracks=tracks_urls)

    def add_track(self, tracks_url):
        self.sp.current_user_saved_tracks_add(tracks=[tracks_url])

    def add_found_track(self, text):
        res_search = self.search_in_spoti(text)
        if res_search is not None:
            self.add_track(res_search[0]['external_urls']['spotify'])
        return res_search is not None

    def add_tracks_from_vk_to_spot(self):
        print('Идёт чтение ваших треков в VK и Spotify...')
        added_tracks = list()
        not_added = list()
        tracks_vk = self.audio_dic_vk()
        # print(tracks_vk)
        tracks_sp = self.audio_dic_sp()
        length = length_dic(tracks_sp)
        # print(tracks_sp)
        print('Начинаем импорт треков в Spotify..')
        for artist, tracks in tracks_vk.items():
            if artist not in tracks_sp.keys():
                for track in tracks:
                    full_name = artist + ' - ' + track
                    check_adding = self.add_found_track(full_name)
                    if check_adding is not None:
                        added_tracks.append(full_name)
                        print(f'Добавлено: {full_name} ({len(added_tracks)}/{length})')
                    else:
                        not_added.append(full_name)
            else:
                for track in tracks:
                    if track not in tracks_sp[artist]:
                        full_name = artist + ' ' + track
                        check_adding = self.add_found_track(full_name)
                        if check_adding is not None:
                            added_tracks.append(full_name)
                            print(f'Добавлено: {full_name} ({len(added_tracks)}/{length})')
                        else:
                            not_added.append(full_name)
        return {
            'added tracks': added_tracks,
            'length': len(added_tracks),
            'not added': not_added
        }


if __name__ == '__main__':
    login = input("Login VK: ")
    password = input("Password VK: ")
    mus = ImportFromVKtoSpotify(login, password)
    mus.add_tracks_from_vk_to_spot()
    end = input()