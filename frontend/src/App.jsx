import { useState } from "react";
import "./App.css";
import LoginScreen from "./components/LoginScreen";
import SelectionScreen from "./components/SelectionScreen";
import QuizScreen from "./components/QuizScreen";

function App() {
	const [screen, setScreen] = useState("login");
	const [user, setUser] = useState(null);
	const [exam, setExam] = useState(null);
	const [subject, setSubject] = useState(null);
	const [chapter, setChapter] = useState(null);
	const [quizId, setQuizId] = useState(null);

	function handleLogin(selectedUser) {
		setUser(selectedUser);
		setScreen("select");
	}

	function handleSelect(selectedExam, selectedSubject, selectedChapter) {
		setExam(selectedExam);
		setSubject(selectedSubject);
		setChapter(selectedChapter);
		setQuizId(crypto.randomUUID());
		setScreen("quiz");
	}

	function handleFinish() {
		setExam(null);
		setSubject(null);
		setChapter(null);
		setQuizId(null);
		setScreen("select");
	}

	function handleLogout() {
		setUser(null);
		setScreen("login");
	}

	return (
		<div className="app">
			{screen === "login" && <LoginScreen onLogin={handleLogin} />}
			{screen === "select" && (
				<SelectionScreen onSelect={handleSelect} onBack={handleLogout} />
			)}
			{screen === "quiz" && (
				<QuizScreen
					user={user}
					exam={exam}
					subject={subject}
					chapter={chapter}
					quizId={quizId}
					onFinish={handleFinish}
					onBack={handleFinish}
				/>
			)}
		</div>
	);
}

export default App;
