from container import send_dispatcher

if __name__ == '__main__':
    delay = 1
    frequency = 2
    send_dispatcher.send_data_to_goggle_sheet(delay=delay,
                                              frequency=frequency)
