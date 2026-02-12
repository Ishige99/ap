.PHONY: extract clean

extract: ap_questions_1000.json

ap_questions_1000.json: extract_ap_questions.py past_exams/markdown/*_ap/*_ap.md
	python3 extract_ap_questions.py

clean:
	rm -f ap_questions_1000.json
