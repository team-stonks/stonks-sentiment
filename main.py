import grpc
import stonks_pb2
import stonks_pb2_grpc

companies = ["INTC", "APPL", "GOOG", "AMD", "TSM", "AMAZN", "NVDA", "TSLA", "MSFT", "FB",]

def get_priority(client, company):
    resp = client.GetCompanyStats(stonks_pb2.CompanyStatsRequest(Figi=company))
    return resp.FreeCashFlow

def get_top_five(client):
    return list(sorted(companies, key=lambda c: get_priority(client, c)))[:5]

def get_rating(company):
    return 10

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

main()