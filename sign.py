import wiringpi

def sign_setup():
    wiringpi.wiringPiSetupGpio()
    for input in [17, 18, 27]:
        wiringpi.pinMode(input, wiringpi.INPUT)
    for switch_pin in [17, 27]:
        wiringpi.pullUpDnControl(switch_pin, wiringpi.PUD_DOWN)



def sign_json():
    return {
        'switch': {
            'one_on': wiringpi.digitalRead(27),
            'two_on': wiringpi.digitalRead(17),
        },
        'door': wiringpi.digitalRead(18)
    }
