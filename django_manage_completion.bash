_mg()
{
	local cur=${COMP_WORDS[COMP_CWORD]}
	COMPREPLY=( $(compgen -W "startapp 0.0.0.0:9000 makemigrations migrate
			runserver createsuperuser shell collectstatic loaddata
			dumpdata>fixtures/db.json sqlmigrate help --database= test
			fixtures/db.json compilemessages" -- $cur) )
}
complete -o dirnames -F _mg mg
