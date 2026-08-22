import { useState, useEffect } from "react";
import { fetchUsers } from "../api";

export default function LoginScreen({ onLogin }) {
	const [users, setUsers] = useState([]);
	const [query, setQuery] = useState("");
	const [loading, setLoading] = useState(true);

	useEffect(() => {
		fetchUsers().then((data) => {
			setUsers(data);
			setLoading(false);
		});
	}, []);

	const filtered = users.filter((u) =>
		u.username.toLowerCase().includes(query.toLowerCase()),
	);

	if (loading) return <div className="loading">Loading users...</div>;

	return (
		<div className="login-screen">
			<h2>Quiz App</h2>
			<p>Select your profile to continue</p>
			<div className="search-bar">
				<input
					type="text"
					placeholder="Search users..."
					value={query}
					onChange={(e) => setQuery(e.target.value)}
					className="search-input"
					autoFocus
				/>
			</div>
			<div className="user-list">
				{filtered.map((user) => (
					<div
						key={user._id}
						className="user-item"
						onClick={() => onLogin(user)}
					>
						<div className="user-item-avatar">
							{user.username[0].toUpperCase()}
						</div>
						<span className="user-item-name">{user.username}</span>
					</div>
				))}
				{filtered.length === 0 && (
					<p
						style={{
							color: "#8696a0",
							fontSize: 13,
							textAlign: "center",
							padding: 16,
						}}
					>
						No users found
					</p>
				)}
			</div>
		</div>
	);
}
