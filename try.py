from models.statistics import Statistics
from google_sheets_services.statistics_sheets_service import StatisticsSheetsService
from datetime import date

stats = Statistics()
service = StatisticsSheetsService()

# stats.date = str(date.today())
username = 'as7rum'
# stats.city = 'Санкт-Петербург'
# stats.location = 'Юбилейный'
# stats.approaches = '62'
# stats.shorts = '10'
# stats.closings = '2'
# stats.forms = '0'
# stats.trust_pays = '0'
# stats.supporters = '0'
# stats.comments = 'Было холодно и мало людей'

# service.add_statistics(stats)

person_stats = service.get_statistics_by_person_username(username)
person_statistics = list(filter(lambda x: x.date == str(date.today()), person_stats))
print (person_statistics)
