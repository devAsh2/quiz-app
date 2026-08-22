import { useState, useEffect } from "react";
import { fetchExams } from "../api";

export default function SelectionScreen({ onSelect, onBack }) {
	const [exams, setExams] = useState([]);
	const [selectedExam, setSelectedExam] = useState(null);
	const [selectedSubject, setSelectedSubject] = useState(null);
	const [loading, setLoading] = useState(true);

	useEffect(() => {
		fetchExams().then((data) => {
			setExams(data);
			setLoading(false);
		});
	}, []);

	if (loading) return <div className="loading">Loading...</div>;

	// Chapter selection
	if (selectedSubject) {
		return (
			<>
				<div className="header">
					<button className="back-btn" onClick={() => setSelectedSubject(null)}>
						&larr;
					</button>
					<div className="header-info">
						<h2>{selectedSubject.name}</h2>
						<p>Select a chapter</p>
					</div>
				</div>
				<div className="selection-list">
					{selectedSubject.chapters.map((ch) => (
						<div
							key={ch.id}
							className="selection-item"
							onClick={() => onSelect(selectedExam, selectedSubject, ch)}
						>
							{ch.name}
						</div>
					))}
				</div>
			</>
		);
	}

	// Subject selection
	if (selectedExam) {
		return (
			<>
				<div className="header">
					<button className="back-btn" onClick={() => setSelectedExam(null)}>
						&larr;
					</button>
					<div className="header-info">
						<h2>{selectedExam.name}</h2>
						<p>Select a subject</p>
					</div>
				</div>
				<div className="selection-list">
					{selectedExam.subjects.map((sub) => (
						<div
							key={sub.id}
							className="selection-item"
							onClick={() => setSelectedSubject(sub)}
						>
							{sub.name}
						</div>
					))}
				</div>
			</>
		);
	}

	// Exam selection
	return (
		<>
			<div className="header">
				<button className="back-btn" onClick={onBack}>
					&larr;
				</button>
				<div className="header-info">
					<h2>Exams</h2>
					<p>Select an exam to begin</p>
				</div>
			</div>
			<div className="selection-list">
				{exams.map((exam) => (
					<div
						key={exam._id || exam.id}
						className="selection-item"
						onClick={() => setSelectedExam(exam)}
					>
						{exam.name}
					</div>
				))}
			</div>
		</>
	);
}
