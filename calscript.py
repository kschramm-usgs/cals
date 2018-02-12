import datetime
import glob
import os
import struct

from obspy.core import UTCDateTime

import sys


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def process_calibrations(start_year, start_day, end_year, end_day):
    start_date = datetime.datetime.strptime(start_year + ' ' + start_day, '%Y %j')
    end_date = datetime.datetime.strptime(end_year + ' ' + end_day, '%Y %j')

    filepaths = find_files(start_date, end_date)

    calibrations = find_calibrations([filepath for sublist in filepaths for filepath in sublist])
    print("network,station,location,channel,calInput,CalBlockette,start,end,filename")
    for cal in calibrations:
        network_code = cal["network"]
        station_code = cal["station"]
        location_code = cal["location"]
        channel_code = cal["channel"]
        cal_input=cal["channel_input"]
        sin_per=cal["signal_period"]
        type = cal["type"]

        start_time = cal["start_time"]
        end_time = start_time + datetime.timedelta(seconds=get_end_time_delta_seconds(cal))

        start_time = start_time.strftime('%Y-%j %H:%M:%S')
        end_time = end_time.strftime('%Y-%j %H:%M:%S')

        file_name = cal["file_name"]
        
        print(
            network_code + "," + station_code + "," + location_code + "," + channel_code + ","+cal_input+"," + str(type) + "," + str(start_time) + "," + str(end_time) + "," + file_name)


def find_files(start_date, end_date):
    """Find the files that may contain calibrations"""
    date = start_date
    filepaths = []
    while date <= end_date:
        eprint("Searching "+str(date)+" until "+str(end_date))
        filepath = '/msd/*_*/%s/%s/*[BE]H*.512.seed' % (date.strftime('%Y'), date.strftime('%j'))
        filepaths.append(glob.glob(filepath))
        # output.append(add_calibrations(dataless, cals))
        date += datetime.timedelta(1)
    return filepaths


def find_calibrations(filepaths):
    """Attempts to retrieve calibrations by looking for calibration blockettes (300, 310, 320)"""
    # mostly written by Adam Ringler
    calibrations = []
    length = len(filepaths)
    curIndex = 0
    for filepath in filepaths:
        curIndex += 1
        eprint("Parsing " + str(curIndex) + " of " + str(length))
        _, _, net_sta, year, jday, loc_chan_reclen_seed = filepath.split('/')
        date = UTCDateTime(year + jday)
        net, sta = net_sta.split('_')
        loc, chan = loc_chan_reclen_seed.split('.')[0].split('_')
        # read the first file and get the record length from blockette 1000
        fh = open(filepath, 'rb')
        record = fh.read(256)
        index = struct.unpack('>H', record[46:48])[0]
        file_stats = os.stat(filepath)
        try:
            record_length = 2 ** struct.unpack('>B', record[index + 6:index + 7])[0]
            # get the total number of records
            total_records = file_stats.st_size // record_length
            # now loop through the records and look for calibration blockettes
            for rec_idx in range(0, total_records):
                fh.seek(rec_idx * record_length, 0)
                record = fh.read(record_length)
                next_blockette = struct.unpack('>H', record[46:48])[0]
                while next_blockette != 0:
                    index = next_blockette
                    blockette_type, next_blockette = struct.unpack('>HH', record[index:index + 4])
                    if blockette_type in (300, 310, 320, 390):
                        year, jday, hour, minute, sec, _, tmsec, _, calFlags, duration = struct.unpack('>HHBBBBHBBL',
                                                                                                       record[
                                                                                                       index + 4:index + 20])
                        stime = UTCDateTime(year=year, julday=jday, hour=hour, minute=minute, second=sec)
                        if blockette_type == 300:
                            # blockette for step cals
                            numStepCals, _, _, intervalDuration, amplitude, calInput = struct.unpack('>BBLLf3s', record[
                                                                                                                 index + 14:index + 31])
                            calibrations.append(
                                {'network': str(net), 'station': str(sta), 'location': str(loc), 'channel': str(chan),
                                 'date': str(date), 'type': 300,
                                 'start_time': UTCDateTime(stime).datetime, 'flags': str(calFlags),
                                 'num_step_cals': int(numStepCals),
                                 'step_duration': int(duration), 'interval_duration': int(intervalDuration),
                                 'amplitude': str(amplitude), 'channel_input': str(calInput.decode("ascii")),
                                 'file_name': str(filepath)})
                        if blockette_type == 310:
                            # blockette for sine cals
                            signalPeriod, amplitude, calInput = struct.unpack('>ff3s', record[index + 20:index + 31])
                            calibrations.append(
                                {'network': str(net), 'station': str(sta), 'location': str(loc), 'channel': str(chan),
                                 'date': str(date), 'type': 310,
                                 'start_time': UTCDateTime(stime).datetime, 'flags': str(calFlags),
                                 'cal_duration': int(duration),
                                 'signal_period': str(signalPeriod), 'amplitude': str(amplitude),
                                 'channel_input': str(calInput.decode("ascii")),
                                 'file_name': str(filepath)})
                        if blockette_type == 320:
                            # blockette for psuedorandom cals
                            amplitude, calInput = struct.unpack('>f3s', record[index + 20:index + 27])
                            calibrations.append(
                                {'network': str(net), 'station': str(sta), 'location': str(loc), 'channel': str(chan),
                                 'date': str(date), 'type': 320,
                                 'start_time': UTCDateTime(stime).datetime, 'flags': str(calFlags),
                                 'cal_duration': int(duration),
                                 'ptp_amplitude': str(amplitude), 'channel_input': str(calInput.decode("ascii")),
                                 'file_name': str(filepath)})
                        if blockette_type == 390:
                            # blockette for generic cals, currently unused
                            amplitude, calInput = struct.unpack('>f3s', record[index + 20:index + 27])
                            calibrations.append(
                                {'network': str(net), 'station': str(sta), 'location': str(loc), 'channel': str(chan),
                                 'date': str(date), 'type': 390,
                                 'start_time': UTCDateTime(stime).datetime, 'flags': str(calFlags),
                                 'cal_duration': int(duration),
                                 'amplitude': str(amplitude), 'channel_input': str(calInput.decode("ascii")),
                                 'file_name': str(filepath)})

        except:
            pass
        fh.close()
    return calibrations


def java_time(datetime):
    return int(datetime.timestamp() * 1000)


def get_end_time_delta_seconds(calibration):
    if calibration['type'] == 300:
        step_delta = calibration['num_step_cals'] * calibration["step_duration"]
        interval_delta = calibration['num_step_cals'] * calibration["interval_duration"]
        seed_delta = step_delta + interval_delta
    else:
        seed_delta = calibration['cal_duration']
    # 0.0001 second ticks to seconds
    return seed_delta / 10000


process_calibrations("2018", "037", "2018", "038")


