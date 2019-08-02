shopt -s globstar dotglob
# convert all pdfs to png
for f in **/*; do
	if [ ${f: -4} == ".pdf" ]; then
		n=${f:0:-4}
		# only convert if png is not present yet
		if [ ! -f $n.png ]; then
			inkscape -d 300 -e $n.png $n.pdf;
			printf ":%s:\n" "$f";
		fi
	fi
done

# convert all pngs to jpg if not present yet
for f in **/*; do
	if [ ${f: -4} == ".png" ]; then
		n=${f:0:-4}
		# only convert if jpg is not present yet
		if [ ! -f $n.jpg ]; then
			convert $n.png -background white -flatten -alpha off $n.jpg
		fi;
	fi
done
