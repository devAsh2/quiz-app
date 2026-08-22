import { useState, useEffect } from "react";
import { fetchLearningVelocity, fetchQuestionDifficulty } from "../api";

export default function AnalyticsScreen({ onBack }) {
	const [tab, setTab] = useState("velocity");
	const [velocityData, setVelocityData] = useState([]);
	const [difficultyData, setDifficultyData] = useState([]);
	const [loading, setLoading] = useState(true);

	useEffect(() => {
		Promise.all([fetchLearningVelocity(), fetchQuestionDifficulty()]).then(
			([vel, diff]) => {
				setVelocityData(vel);
				setDifficultyData(diff);
				setLoading(false);
			},
		);
	}, []);

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
					Velocity
				</button>
				<button
					className={`tab ${tab === "difficulty" ? "tab-active" : ""}`}
					onClick={() => setTab("difficulty")}
				>
					Difficulty
				</button>
			</div>

			<div className="analytics-content">
				{tab === "velocity" && (
					<div className="analytics-list">
						{velocityData.length === 0 && (
							<p className="empty-msg">No data yet. Take some quizzes first.</p>
						)}
						{velocityData.map((user, i) => (
							<div key={user.user_id} className="analytics-card">
								<div className="analytics-rank">#{i + 1}</div>
								<div className="analytics-details">
									<div className="analytics-name">{user.user_id}</div>
									<div className="analytics-metrics">
										<span>Accuracy: {(user.accuracy * 100).toFixed(1)}%</span>
										<span>Speed: {user.avg_response_time.toFixed(1)}s</span>
										<span>
											Consistency: {(user.consistency_score * 100).toFixed(1)}%
										</span>
									</div>
								</div>
								<div className="analytics-score">
									{(user.learning_velocity_index * 100).toFixed(0)}
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
			</div>
		</>
	);
}
