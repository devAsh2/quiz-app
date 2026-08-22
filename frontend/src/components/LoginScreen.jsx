import { useState, useEffect } from "react";
import { fetchUsers } from "../api";

export default function LoginScreen({ onLogin }) {
	const [users, setUsers] = useState([]);
	const [loading, setLoading] = useState(true);

	useEffect(() => {
		fetchUsers().then((data) => {
			setUsers(data);
			setLoading(false);
		});
	}, []);

	if (loading) return <div className="loading">Loading users...</div>;

	return (
		<div className="login-screen">
			<h2>Quiz App</h2>
			<p>Select your profile to continue</p>
			<div className="user-list">
				{users.map((user) => (
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
			</div>
		</div>
	);
}
