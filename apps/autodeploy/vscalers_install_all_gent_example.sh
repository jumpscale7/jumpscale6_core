
python vscalers_basenode.py -r 10.101.175.1 -s rooter -p rooter -g 241 -c vscalers_computenode -t platform,core,configure
python vscalers_basenode.py -r 10.101.175.2 -s rooter -p rooter -g 241 -c vscalers_computenode -t platform,core,configure
#python vscalers_basenode.py -r 10.101.175.3 -s rooter -p rooter -g 241 -c vscalers_computenode -t platform,core,configure
python vscalers_basenode.py -r 10.101.175.4 -s rooter -p rooter -g 241 -c vscalers_computenode -t platform,core,configure
python vscalers_basenode.py -r 10.101.175.5 -s rooter -p rooter -g 241 -c vscalers_computenode -t platform,core,configure
python vscalers_basenode.py -r 10.101.175.6 -s rooter -p rooter -g 241 -c vscalers_computenode -t platform,core,configure

python vscalers_master.py -r 10.101.175.1 -p rooter --ipaddr=10.101.175.200/16




