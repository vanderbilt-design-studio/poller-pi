import wiringpi

def sign_setup():
    wiringpi.wiringPiSetupGpio()
    for input in [17, 18, 27]:
        wiringpi.pinMode(input, wiringpi.INPUT)



def sign_json():
    return {
        'switch': {
            'one_on': wiringpi.digitalRead(27),
            'two_on': wiringpi.digitalRead(17),
        },
        'door': wiringpi.digitalRead(18)
    }
