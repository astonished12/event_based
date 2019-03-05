from settings import channel, total_msgs, r
import sys
import datetime


#{(patient-name,"Smith");(DoB,"10.08.1930");(height,1.75);(eye-color,"brown");(heart-rate,80)}
if __name__ == '__main__':
    name = sys.argv[1]

    print('Welcome to {channel}'.format(**locals()))
    count_send_msgs = 0
    while count_send_msgs < total_msgs:
        data = []
        data.append(("patient-name", "Smith"))
        data.append(("DoB",  str(datetime.datetime.now())))
        data.append(("height", "1.75"))

        message = ' '.join(str(e[0]+" "+e[1]) for e in data)      
        message = '{name} says: {message}'.format(**locals())

        print(message)
        r.publish(channel, message)
        count_send_msgs += 1