import { useState, useEffect } from "react";
import {
	fetchLearningVelocity,
	fetchQuestionDifficulty,
	fetchWeakAreas,
} from "../api";

export default function AnalyticsScreen({ user, onBack }) {
	const [tab, setTab] = useState("velocity");
	const [velocityData, setVelocityData] = useState([]);
	const [difficultyData, setDifficultyData] = useState([]);
	const [weakAreaData, setWeakAreaData] = useState([]);
	const [loading, setLoading] = useState(true);

	useEffect(() => {
		const promises = [fetchLearningVelocity(), fetchQuestionDifficulty()];
		if (user) promises.push(fetchWeakAreas(user._id));
		Promise.all(promises).then(([vel, diff, weak = []]) => {
			setVelocityData(vel);
			setDifficultyData(diff);
			setWeakAreaData(weak);
			setLoading(false);
		});
	}, [user]);

	if (loading) return <div className="loading">Loading analytics...</div>;

	return (
		<>
			<div className="header">
				<button className="back-btn" onClick={onBack}>
					&larr;
				</button>
				<div className="header-info">
					<h2>Analytics</h2>
					<p>Performance insights</p>
				</div>
			</div>

			<div className="tabs">
				<button
					className={`tab ${tab === "velocity" ? "tab-active" : ""}`}
					onClick={() => setTab("velocity")}
				>
					Learning Velocity
				</button>
				<button
					className={`tab ${tab === "difficulty" ? "tab-active" : ""}`}
					onClick={() => setTab("difficulty")}
				>
					Question Difficulty
				</button>
				{user && (
					<button
						className={`tab ${tab === "weakareas" ? "tab-active" : ""}`}
						onClick={() => setTab("weakareas")}
					>
						Weak Areas
					</button>
				)}
			</div>

			<div className="tab-description">
				{tab === "velocity" &&
					"Ranks all users by a weighted score of accuracy, response speed, and consistency."}
				{tab === "difficulty" &&
					"Ranks questions from hardest to easiest based on accuracy and response time across all attempts."}
				{tab === "weakareas" &&
					"Your personal chapter breakdown — lowest accuracy chapters appear first."}
			</div>

			<div className="analytics-content">
				{tab === "velocity" && (
					<div className="analytics-list">
						{velocityData.length === 0 && (
							<p className="empty-msg">No data yet. Take some quizzes first.</p>
						)}
						{velocityData.map((u, i) => (
							<div key={u.user_id} className="analytics-card">
								<div className="analytics-rank">#{i + 1}</div>
								<div className="analytics-details">
									<div className="analytics-name">{u.user_id}</div>
									<div className="analytics-metrics">
										<span>Accuracy: {(u.accuracy * 100).toFixed(1)}%</span>
										<span>Speed: {u.avg_response_time.toFixed(1)}s</span>
										<span>
											Consistency: {(u.consistency_score * 100).toFixed(1)}%
										</span>
									</div>
								</div>
								<div className="analytics-score">
									{(u.learning_velocity_index * 100).toFixed(0)}
								</div>
							</div>
						))}
					</div>
				)}

				{tab === "difficulty" && (
					<div className="analytics-list">
						{difficultyData.length === 0 && (
							<p className="empty-msg">No data yet. Take some quizzes first.</p>
						)}
						{difficultyData.map((q, i) => (
							<div key={q.question_id} className="analytics-card">
								<div className="analytics-rank">#{i + 1}</div>
								<div className="analytics-details">
									<div className="analytics-name">{q.question_id}</div>
									<div className="analytics-metrics">
										<span>Accuracy: {q.accuracy_percentage.toFixed(1)}%</span>
										<span>Avg Time: {q.avg_response_time.toFixed(1)}s</span>
										<span>Attempts: {q.total_attempts}</span>
									</div>
								</div>
								<div className="analytics-score">
									{q.difficulty_score.toFixed(0)}
								</div>
							</div>
						))}
					</div>
				)}

				{tab === "weakareas" && (
					<div className="analytics-list">
						{weakAreaData.length === 0 && (
							<p className="empty-msg">No data yet. Take some quizzes first.</p>
						)}
						{weakAreaData.map((item, i) => (
							<div key={item.chapter_id} className="analytics-card">
								<div className="analytics-rank">#{i + 1}</div>
								<div className="analytics-details">
									<div className="analytics-name">{item.chapter_id}</div>
									<div className="analytics-metrics">
										<span>Accuracy: {(item.accuracy * 100).toFixed(1)}%</span>
										<span>Avg Time: {item.avg_response_time.toFixed(1)}s</span>
										<span>Sessions: {item.quiz_sessions}</span>
									</div>
								</div>
								<div
									className="analytics-score"
									style={{
										color:
											item.accuracy < 0.4
												? "#ff4444"
												: item.accuracy < 0.7
													? "#ffa500"
													: "#00a884",
									}}
								>
									{(item.accuracy * 100).toFixed(0)}%
								</div>
							</div>
						))}
					</div>
				)}
			</div>
		</>
	);
}
