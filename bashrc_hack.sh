## astro molaa
isrun=`ps -u tgh | grep python | wc -l`
if [ $isrun -lt 1 ] 
then 
    cd /home/pi/Dev/AST_Molaa
    numbers=$(grep "PINS =\|PINS=" ast_molaa.py | sed 's/[^0-9,]//g' | sed 's/,/ /g')
    for n in ${numbers} 
    do
	gpio export ${n} out
    done

    while [ 1 -le 20 ]
    do
	python ast_molaa.py --inport=8989 --localnetport=8900 --localnet=aeffect07.local --inip=aeffect01.local &
	killpid=$!
	sleep 120
	kill -9 $killpid
    done
fi
