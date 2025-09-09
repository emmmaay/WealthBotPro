
#!/bin/bash
# Script to help you copy files to your Ubuntu server

echo "📁 Files you need to copy to your Ubuntu server:"
echo ""
echo "Copy these files to ~/bsc_sniper_bot_2/ on your Ubuntu server:"
echo ""
echo "Main bot files:"
echo "- bsc_sniper_bot_2.py"
echo "- advanced_security_engine.py"
echo "- blockchain_interface.py"
echo "- profit_management.py"
echo "- telegram_notifier.py"
echo "- validate_key.py"
echo "- config.json"
echo ""
echo "You can use SCP to copy files:"
echo "scp bot_files/* ubuntu@your-server-ip:~/bsc_sniper_bot_2/"
echo ""
echo "Or create them manually on your server using nano/vim"
