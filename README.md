# sunset_update_cron
Update cronjob with latest sunset data

Purpose:
An external light should be switched on at a defined level of twilight
As the time of the sunset and sunrise is different every day, this script runs once a day to calculate the sunset and then updates the start time of the lights-on-job in the crontab. 

Schedule the script itself by using cron
E.g.:
0 */12 * * * python /home/user/light/sunset_update_cron.py

sunset_calc.py
Print Sunset and Sunrise for each day of a year
