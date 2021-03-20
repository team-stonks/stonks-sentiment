import grpc
import stonks_pb2
import stonks_pb2_grpc

from news_sent import company_sentiment

example_companies = ["INTC", "APPL", "GOOG", "AMD", "TSM", "AMAZN", "NVDA", "TSLA", "MSFT", "FB",]


def get_priority(client, company):
    resp = client.GetCompanyStats(stonks_pb2.CompanyStatsRequest(Figi=company))
    return resp.DebtToEquity


def get_top_five(client, companies):
    top_companies = sorted(companies, key=lambda c: get_priority(client, c), reverse=True)[:5]
    return sorted(top_companies, key=lambda c: get_rating(c), reverse=True)


def get_rating(company):
    return company_sentiment(company)


def send_ratings(client, companies):
    name_rating = {}
    for c in companies:
        name_rating[c] = get_rating(c)
    message = str(name_rating)
    client.TelegramNotification(stonks_pb2.TelegramRequest(Message=message))


def main():
    channel = grpc.insecure_channel('localhost:50051')
    stub = stonks_pb2_grpc.StonksApiStub(channel)
    
    top_companies = get_top_five(stub)
    send_ratings(stub, top_companies)


if __name__ == '__main__':
    main()
