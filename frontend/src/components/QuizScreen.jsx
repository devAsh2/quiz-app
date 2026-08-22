import { useState, useEffect, useRef } from "react";
import { fetchQuestions, submitAnswer, fetchResult } from "../api";

export default function QuizScreen({
	user,
	exam,
	subject,
	chapter,
	quizId,
	onFinish,
	onBack,
}) {
	const [questions, setQuestions] = useState([]);
	const [currentIndex, setCurrentIndex] = useState(0);
	const [messages, setMessages] = useState([]);
	const [showOptions, setShowOptions] = useState(false);
	const [submitting, setSubmitting] = useState(false);
	const [quizDone, setQuizDone] = useState(false);
	const [result, setResult] = useState(null);
	const [questionShownTime, setQuestionShownTime] = useState(null);
	const chatRef = useRef(null);

	useEffect(() => {
		fetchQuestions(chapter.id).then((data) => {
			setQuestions(data);
			if (data.length > 0) {
				showQuestion(data[0], 0, data.length);
			}
		});
	}, [chapter.id]);

	useEffect(() => {
		if (chatRef.current) {
			chatRef.current.scrollTop = chatRef.current.scrollHeight;
		}
	}, [messages, showOptions]);

	function showQuestion(q, index, total) {
		const now = new Date().toISOString();
		setQuestionShownTime(now);
		setMessages((prev) => [
			...prev,
			{ type: "system", text: `Question ${index + 1} of ${total}` },
			{ type: "received", text: q.text },
		]);
		setShowOptions(true);
	}

	async function handleOptionSelect(optionIndex) {
		if (submitting) return;
		setSubmitting(true);
		setShowOptions(false);

		const q = questions[currentIndex];
		const submittedTime = new Date().toISOString();

		// Show user's choice as a sent message
		setMessages((prev) => [
			...prev,
			{ type: "sent", text: q.options[optionIndex] },
		]);

		const payload = {
			quiz_id: quizId,
			question_id: q._id || q.id,
			selected_option: optionIndex,
			question_shown_time: questionShownTime,
			answer_submitted_time: submittedTime,
		};

		const res = await submitAnswer(user._id, payload);

		// Show feedback
		const feedback = res.is_correct
			? "✅ Correct!"
			: `❌ Incorrect. Answer: ${q.options[res.correct_option]}`;
		setMessages((prev) => [...prev, { type: "received", text: feedback }]);

		// Move to next or finish
		const nextIndex = currentIndex + 1;
		if (nextIndex < questions.length) {
			setCurrentIndex(nextIndex);
			setTimeout(() => {
				showQuestion(questions[nextIndex], nextIndex, questions.length);
				setSubmitting(false);
			}, 800);
		} else {
			// Quiz complete
			setTimeout(async () => {
				const scoreData = await fetchResult(quizId);
				setResult(scoreData);
				setQuizDone(true);
				setSubmitting(false);
			}, 800);
		}
	}

	const progress =
		questions.length > 0
			? ((currentIndex + (quizDone ? 1 : 0)) / questions.length) * 100
			: 0;

	return (
		<>
			<div className="header">
				<button className="back-btn" onClick={onBack}>
					&larr;
				</button>
				<div className="header-avatar">Q</div>
				<div className="header-info">
					<h2>{chapter.name}</h2>
					<p>
						{exam.name} &middot; {subject.name}
					</p>
				</div>
			</div>

			<div className="progress-bar">
				<div className="progress-bar-fill" style={{ width: `${progress}%` }} />
			</div>

			<div className="chat-area" ref={chatRef}>
				{messages.map((msg, i) => (
					<div key={i} className={`message message-${msg.type}`}>
						{msg.text}
					</div>
				))}

				{quizDone && result && (
					<div className="result-card">
						<h3>Quiz Complete!</h3>
						<div className="result-score">
							{result.score}/{result.total}
						</div>
						<div className="result-percentage">
							{result.percentage.toFixed(1)}%
						</div>
						<button className="btn-primary" onClick={onFinish}>
							Back to Home
						</button>
					</div>
				)}
			</div>

			{showOptions && !quizDone && questions[currentIndex] && (
				<div className="options-container">
					{questions[currentIndex].options.map((opt, i) => (
						<button
							key={i}
							className="option-btn"
							onClick={() => handleOptionSelect(i)}
							disabled={submitting}
						>
							{String.fromCharCode(65 + i)}. {opt}
						</button>
					))}
				</div>
			)}
		</>
	);
}
