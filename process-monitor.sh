# zsh function to operate scripts
# You can add this to your .zshrc file
# e.g.) source /path/to/process-monitor.sh

PROJECT_PATH="$HOME/workspace/process-monitor"
function process_monitor(){
	echo "** Process Monitor **"
	echo "0. List processes & Config"
	echo "1. Delete Terminated Processes"
	echo "2. Add PID for Monitoring"
	echo "3. Delete PID for Monitoring"

	echo -n "Select: "
	read userInput

	case $userInput in 
		0) 
			(cd $PROJECT_PATH && python scan_table.py)
			;;
		1) 
			(cd $PROJECT_PATH && python deregister_terminated.py)
			;;
		2) 
			echo -n "Enter PID: "
			read pid
			(cd $PROJECT_PATH && python register_pid.py $pid)
			;;
		3) 
			echo -n "Enter PID: "
			read pid
			(cd $PROJECT_PATH && python deregister_pid.py $pid)
			;;
	esac
}

