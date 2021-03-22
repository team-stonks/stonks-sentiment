import grpc
import stonks_pb2
import stonks_pb2_grpc

from news_sent import company_sentiment
from company_dict import company_map


def get_priority(client, company):
    resp = client.GetCompanyStats(stonks_pb2.CompanyStatsRequest(Figi=company))
    return resp.DebtToEquity


def get_top_five(client, companies):
    top_companies = sorted(companies, key=lambda c: get_priority(client, c), reverse=True)[:5]
    top_companies = [company_map.get(c, "S&P 500") for c in top_companies]
    top_companies = [(c, get_rating(c)) for c in top_companies]
    return sorted(top_companies, key=lambda c: c[1], reverse=True)


def get_rating(company):
    return company_sentiment(company)


def send_ratings(client, companies):
    message = ''
    for i, (name, score) in enumerate(companies):
        message += f"{i+1}. {name}, sentiment score: {score}.\n"
    message += 'Good luck!'
    client.TelegramNotification(stonks_pb2.TelegramRequest(Message=message))


def main():
    channel = grpc.insecure_channel('localhost:50051')
    stub = stonks_pb2_grpc.StonksApiStub(channel)
    sample_companies = ["INTC", "APPL", "GOOG", "AMD", "TSM", "AMAZN", "NVDA", "TSLA", "MSFT", "FB", ]
    top_companies = get_top_five(stub, sample_companies)
    send_ratings(stub, top_companies)


if __name__ == '__main__':
    main()
