import { useState } from "react";
import TranslateTree from "../i18n";

function AuthScreen({ onAuthenticated, language }) {
  const [mode, setMode] = useState("login");

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [error, setError] = useState("");

  const submitForm = (event) => {
    event.preventDefault();
    setError("");

    const trimmedEmail = email.trim().toLowerCase();

    if (!trimmedEmail || !password) {
      setError("Please enter your email and password.");
      return;
    }

    if (mode === "signup" && !name.trim()) {
      setError("Please enter your name.");
      return;
    }

    const storedUser = JSON.parse(
      localStorage.getItem("sevaUser") || "null"
    );

    if (mode === "signup") {
      const user = {
        name: name.trim(),
        email: trimmedEmail,
        password,
      };

      localStorage.setItem(
        "sevaUser",
        JSON.stringify(user)
      );

      localStorage.setItem(
        "sevaAuthenticated",
        "true"
      );

      onAuthenticated(user);
      return;
    }

    if (!storedUser) {
      setError(
        "No account found. Please create an account first."
      );
      return;
    }

    if (
      storedUser.email !== trimmedEmail ||
      storedUser.password !== password
    ) {
      setError("Incorrect email or password.");
      return;
    }

    localStorage.setItem(
      "sevaAuthenticated",
      "true"
    );

    onAuthenticated(storedUser);
  };

  return (
    <TranslateTree language={language}>
    <div className="auth-page">
      <div className="auth-left-panel">
        <div className="auth-visual-art" aria-hidden="true">
          <svg viewBox="0 0 520 420" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="278" cy="215" r="154" fill="url(#sevaSun)" fillOpacity=".2" />
            <circle cx="278" cy="215" r="139" stroke="#F4D58E" strokeOpacity=".56" />
            <circle cx="278" cy="215" r="112" stroke="#F4D58E" strokeOpacity=".24" strokeDasharray="3 8" />
            <path d="M62 330C133 270 198 265 264 303C332 342 385 339 458 263" stroke="#F7E9C4" strokeOpacity=".48" strokeWidth="2" />
            <path d="M47 355C128 296 199 295 267 332C337 370 399 365 477 290" stroke="#E9855F" strokeOpacity=".74" strokeWidth="3" />
            <path d="M84 379C150 334 216 327 275 357C340 391 398 391 448 347" stroke="#F7E9C4" strokeOpacity=".26" strokeWidth="1.5" />
            <circle cx="278" cy="215" r="69" fill="#F4C66C" />
            <circle cx="278" cy="194" r="17" fill="#1B5947" />
            <path d="M241 257C246 229 259 216 278 216C297 216 310 229 315 257C297 269 259 269 241 257Z" fill="#1B5947" />
            <circle cx="278" cy="215" r="84" stroke="#FFF8E8" strokeOpacity=".72" strokeWidth="1.5" />
            <g transform="rotate(8 428 285)">
              <rect x="356" y="244" width="128" height="82" rx="18" fill="#F5E7C7" />
              <circle cx="386" cy="274" r="11" fill="#2E8064" />
              <path d="M381 274L385 278L392 269" stroke="#FFF9EB" strokeWidth="2.3" strokeLinecap="round" strokeLinejoin="round" />
              <rect x="407" y="269" width="58" height="6" rx="3" fill="#285A48" fillOpacity=".6" />
              <rect x="379" y="298" width="83" height="5" rx="2.5" fill="#285A48" fillOpacity=".16" />
            </g>
            <circle cx="407" cy="103" r="7" fill="#E9855F" />
            <circle cx="142" cy="254" r="5" fill="#F4C66C" />
            <defs>
              <radialGradient id="sevaSun" cx="0" cy="0" r="1" gradientTransform="matrix(0 154 -154 0 278 215)" gradientUnits="userSpaceOnUse">
                <stop stopColor="#F4C66C" />
                <stop offset="1" stopColor="#F4C66C" stopOpacity="0" />
              </radialGradient>
            </defs>
          </svg>
        </div>
        <div className="auth-brand">
          <div className="brand-mark">S</div>

          <div>
            <strong>SEVA AI</strong>
            <span>Government benefits, made simpler.</span>
          </div>
        </div>

        <div className="auth-left-content">
          <div className="auth-eyebrow">
            AI-POWERED CITIZEN ASSISTANCE
          </div>

          <h1>
            One conversation.
            <br />
            <span>Better access to support.</span>
          </h1>

          <p>
            Discover government schemes, understand your
            eligibility, prepare documents, and get guided
            through the process in one place.
          </p>

          <div className="auth-feature-list">
            <div className="auth-feature">
              <span className="feature-number">01</span>
              <div>
                <strong>Tell us your situation</strong>
                <p>
                  Speak naturally in your selected language.
                </p>
              </div>
            </div>

            <div className="auth-feature">
              <span className="feature-number">02</span>
              <div>
                <strong>Find relevant schemes</strong>
                <p>
                  Get scheme information based on your
                  circumstances.
                </p>
              </div>
            </div>

            <div className="auth-feature">
              <span className="feature-number">03</span>
              <div>
                <strong>Understand what you need</strong>
                <p>
                  See eligibility, documents and next steps.
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="auth-footer">
          <span>SEVA AI</span>
          <span>Prototype</span>
        </div>
      </div>

      <div className="auth-right-panel">
        <div className="auth-card">
          <div className="auth-card-heading">
            <div className="auth-mobile-brand">
              <div className="brand-mark">S</div>
              <strong>SEVA AI</strong>
            </div>

            <h2>
              {mode === "login"
                ? "Welcome back"
                : "Create your account"}
            </h2>

            <p>
              {mode === "login"
                ? "Sign in to continue your SEVA AI journey."
                : "Create a simple account to get started."}
            </p>
          </div>

          <div className="auth-tabs">
            <button
              type="button"
              className={
                mode === "login"
                  ? "auth-tab active"
                  : "auth-tab"
              }
              onClick={() => {
                setMode("login");
                setError("");
              }}
            >
              Sign in
            </button>

            <button
              type="button"
              className={
                mode === "signup"
                  ? "auth-tab active"
                  : "auth-tab"
              }
              onClick={() => {
                setMode("signup");
                setError("");
              }}
            >
              Create account
            </button>
          </div>

          <form
            className="auth-form"
            onSubmit={submitForm}
          >
            {mode === "signup" && (
              <label>
                Full name
                <input
                  type="text"
                  placeholder="Enter your full name"
                  value={name}
                  onChange={(event) =>
                    setName(event.target.value)
                  }
                />
              </label>
            )}

            <label>
              Email address
              <input
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(event) =>
                  setEmail(event.target.value)
                }
              />
            </label>

            <label>
              Password
              <input
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(event) =>
                  setPassword(event.target.value)
                }
              />
            </label>

            {mode === "login" && (
              <div className="auth-extra-row">
                <label className="checkbox-row">
                  <input
                    type="checkbox"
                    defaultChecked
                  />
                  <span>Remember me</span>
                </label>

                <button
                  type="button"
                  className="text-button"
                  onClick={() =>
                    setError(
                      "Password recovery will be added in the next version."
                    )
                  }
                >
                  Forgot password?
                </button>
              </div>
            )}

            {error && (
              <div className="auth-error">
                {error}
              </div>
            )}

            <button
              type="submit"
              className="auth-submit"
            >
              {mode === "login"
                ? "Continue to SEVA AI"
                : "Create account"}
              <span>→</span>
            </button>
          </form>

          <div className="auth-divider">
            <span>Secure prototype access</span>
          </div>

          <p className="auth-disclaimer">
            Your information is used to personalize your
            SEVA AI experience. This prototype does not use
            production authentication or payment services.
          </p>
        </div>
      </div>
    </div>
    </TranslateTree>
  );
}

export default AuthScreen;
