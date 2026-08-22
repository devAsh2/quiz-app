const API_BASE = import.meta.env.VITE_API_URL;

export async function fetchUsers() {
	const res = await fetch(`${API_BASE}/users`);
	return res.json();
}

export async function fetchExams() {
	const res = await fetch(`${API_BASE}/exams`);
	return res.json();
}

export async function fetchQuestions(chapterId) {
	const res = await fetch(`${API_BASE}/questions/${chapterId}`);
	return res.json();
}

export async function submitAnswer(userId, payload) {
	const res = await fetch(`${API_BASE}/submit`, {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			"X-User-Id": userId,
		},
		body: JSON.stringify(payload),
	});
	return res.json();
}

export async function fetchResult(quizId) {
	const res = await fetch(`${API_BASE}/result/${quizId}`);
	return res.json();
}
