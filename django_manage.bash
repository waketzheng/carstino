_mg()    
{  
	local cur=${COMP_WORDS[COMP_CWORD]}    
	COMPREPLY=( $(compgen -W "startapp 0.0.0.0:9000 makemigrations migrate   
			runserver createsuperuser shell collectstatic loaddata   
			dumpdata>db.json sqlmigrate help --database= test   
			" -- $cur) )  
}    
complete -o dirnames -F _mg mg  
