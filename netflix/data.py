import pdb
import re

class NetflixMovieData:
  def __init__(self, **kwargs):
    self.run_time = kwargs.get('run_time', 0)
    self.name = kwargs.get('name', '')
    self.year = kwargs.get('year', '')
    return

  def __str__(self):
    return '"{}", {}, {}'.format(self.name, self.year, self.run_time)

class NetflixShowData:
  time_pattern = re.compile('([0-9]h\s)?([0-9]+m)')

  def __init__(self, **kwargs):
    self.seasons = ''
    self.number_of_episodes = kwargs.get('number_of_episodes', '')
    self.run_time = kwargs.get('run_time', 0)
    self.name = kwargs.get('name', '')
    self.year = kwargs.get('year', '')
    self.episode_data = kwargs.get('episode_data', {})

    if self.episode_data:
      self.seasons = len(self.episode_data)
      self.number_of_episodes = self._get_episode_count()
      self.run_time = self._get_total_episode_time()
    return

  def __str__(self):
    return '{} ({}): {} Seasons, {} Episodes {}'.format(self.name,
                                                        self.year,
                                                        self.seasons,
                                                        self.number_of_episodes,
                                                        self.run_time)
  def _get_episode_count(self):
    return sum([len(season['episodes']) for season in self.episode_data])

  def _get_total_episode_time(self):
    total_hours = 0
    total_minutes = 0

    for season in self.episode_data:
      for episode in season['episodes']:

        matches = self.time_pattern.match(episode.run_time)
        hours, minutes = matches.group(0), matches.group(1)
        hours = hours.strip().replace('h', '')
        if minutes:
          minutes = int(minutes.replace('m', ''))
          hours = int(hours)
        else:
          minutes = int(hours.replace('m', ''))
          hours = 0

        total_hours += hours
        total_minutes += minutes

      total_hours += total_minutes / 60
      total_minutes = total_minutes % 60

    if total_hours:
      hours_str = '{}h'.format(total_hours)
    else:
      hours_str = ''

    return hours_str + '{}m'.format(total_minutes)

class NetflixEpisodeData:
  def __init__(self, **kwargs):
    self.description = kwargs.get('description', '')
    self.run_time = kwargs.get('run_time', 0)
    self.title = kwargs.get('title', '')
    return

  def __str__(self):
    return '"{}", {}'.format(self.title, self.run_time)

class NetflixDataConverter:
  pattern = re.compile('([0-9]h\s)?[0-9]+m')
  time_pattern = re.compile('([0-9]h\s)?[0-9]+m')
  title_pattern = re.compile('(.*?)(([0-9]h\s)?[0-9]+m)')

  def convert_to_show_data(self, data_array):
    output = []
    for record in data_array:
      name, description, episode_data = record

      description = description.split('\\n')
      year = description[1]
      time = description[3]
      if self.pattern.match(time):
        output.append(NetflixMovieData(year = year,
                                       run_time = time,
                                       name = name))
      else:
        output.append(NetflixShowData(year = year,
                                      name = name,
                                      episode_data = self._parse_episode_data(episode_data)))
    return output

  def _chunk(self, array, size):
    return list(zip(*[iter(array)] * size))

  def _parse_episode_data(self, episode_data):
    data = []

    for season in episode_data:
      season_data = season.strip().replace('\n\n', '\n').split('\n')
      season_name = season_data.pop(0)
      episodes = []
      ids_seen = []

      for chunk in self._chunk(season_data, 3):
        if chunk[0] not in ids_seen:
          try:
            matches = self.title_pattern.match(chunk[1])
            episodes.append(NetflixEpisodeData(run_time = matches.group(2),
                                               title = matches.group(1),
                                               description = chunk[2]))
            ids_seen.append(chunk[0])
          except AttributeError as e:
            pdb.set_trace()

      data.append({ 'season': season_name, 'episodes': episodes })
    return data