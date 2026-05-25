import React from "react";
import { useEffect, useState } from "react";
import { FiCheckCircle } from "react-icons/fi";
import { api } from "../api/client.js";
import { useAuth } from "../auth/AuthContext.jsx";

export default function SettingsPage() {
  const { user, updateUser } = useAuth();
  const [name, setName] = useState(user?.name || "");
  const [profileBusy, setProfileBusy] = useState(false);
  const [passwordBusy, setPasswordBusy] = useState(false);
  const [profileMessage, setProfileMessage] = useState("");
  const [passwordMessage, setPasswordMessage] = useState("");
  const [profileError, setProfileError] = useState("");
  const [passwordError, setPasswordError] = useState("");
  const [passwords, setPasswords] = useState({
    currentPassword: "",
    newPassword: "",
    confirmPassword: ""
  });

  useEffect(() => {
    setName(user?.name || "");
  }, [user?.name]);

  async function saveProfile(event) {
    event.preventDefault();
    setProfileMessage("");
    setProfileError("");

    if (name.trim().length < 2) {
      setProfileError("Name must be at least 2 characters.");
      return;
    }

    setProfileBusy(true);
    try {
      const response = await api.patch("/auth/me", { name: name.trim() });
      updateUser(response.data);
      setProfileMessage("Account name updated.");
    } catch (err) {
      setProfileError(err.response?.data?.detail || "Could not update account name.");
    } finally {
      setProfileBusy(false);
    }
  }

  async function changePassword(event) {
    event.preventDefault();
    setPasswordMessage("");
    setPasswordError("");

    if (passwords.newPassword.length < 8) {
      setPasswordError("New password must be at least 8 characters.");
      return;
    }
    if (passwords.newPassword !== passwords.confirmPassword) {
      setPasswordError("New password and confirmation do not match.");
      return;
    }

    setPasswordBusy(true);
    try {
      await api.post("/auth/change-password", {
        current_password: passwords.currentPassword,
        new_password: passwords.newPassword
      });
      setPasswords({ currentPassword: "", newPassword: "", confirmPassword: "" });
      setPasswordMessage("Password changed successfully.");
    } catch (err) {
      setPasswordError(err.response?.data?.detail || "Could not change password.");
    } finally {
      setPasswordBusy(false);
    }
  }

  function updatePasswordField(field, value) {
    setPasswords((current) => ({ ...current, [field]: value }));
  }

  return (
    <div className="lf-settings-page">
      <section className="lf-settings-header">
        <div>
          <h1>Settings</h1>
          <p>Manage your account and application preferences</p>
        </div>
      </section>

      <section className="lf-settings-grid">
        <form className="lf-settings-card" onSubmit={saveProfile}>
          <div className="lf-settings-card__title">Account Details</div>

          <label className="lf-settings-field">
            <span>Full Name</span>
            <input className="form-input" value={name} onChange={(event) => setName(event.target.value)} minLength={2} maxLength={120} required placeholder="Your full name" />
          </label>

          <label className="lf-settings-field">
            <span>Email Address</span>
            <input className="form-input" value={user?.email || ""} readOnly />
          </label>

          <label className="lf-settings-field">
            <span>Role</span>
            <input className="form-input" value={user?.role ? `${user.role.charAt(0).toUpperCase()}${user.role.slice(1)}` : "-"} readOnly />
          </label>

          {profileError && <Message tone="error" text={profileError} />}
          {profileMessage && <Message tone="success" text={profileMessage} />}

          <button className="lf-settings-submit" disabled={profileBusy || name.trim() === user?.name} type="submit">
            {profileBusy ? "Saving..." : "Save Changes"}
          </button>
        </form>

        <form className="lf-settings-card" onSubmit={changePassword}>
          <div className="lf-settings-card__title">Password</div>

          <label className="lf-settings-field">
            <span>Current Password</span>
            <input className="form-input" type="password" value={passwords.currentPassword} onChange={(event) => updatePasswordField("currentPassword", event.target.value)} required autoComplete="current-password" />
          </label>

          <label className="lf-settings-field">
            <span>New Password</span>
            <input className="form-input" type="password" value={passwords.newPassword} onChange={(event) => updatePasswordField("newPassword", event.target.value)} minLength={8} required autoComplete="new-password" />
          </label>

          <label className="lf-settings-field">
            <span>Confirm Password</span>
            <input className="form-input" type="password" value={passwords.confirmPassword} onChange={(event) => updatePasswordField("confirmPassword", event.target.value)} minLength={8} required autoComplete="new-password" />
          </label>

          {passwordError && <Message tone="error" text={passwordError} />}
          {passwordMessage && <Message tone="success" text={passwordMessage} />}

          <button className="lf-settings-submit" disabled={passwordBusy} type="submit">
            {passwordBusy ? "Updating..." : "Update Password"}
          </button>
        </form>
      </section>
    </div>
  );
}

function Message({ tone, text }) {
  return (
    <div className={`lf-settings-message lf-settings-message-${tone}`}>
      {tone === "success" && <FiCheckCircle size={16} />}
      <span>{text}</span>
    </div>
  );
}
