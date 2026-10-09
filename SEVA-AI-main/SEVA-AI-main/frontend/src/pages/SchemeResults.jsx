function SchemeResults({ eligibilityResults }) {
  const results = eligibilityResults?.results || [];

  return (
    <div className="scheme-results-screen">
      <header className="conversation-top">
        <div className="brand">
          <div className="brand-icon">S</div>
          <span>SEVA AI</span>
        </div>

        <div className="conversation-status">
          <span className="status-dot"></span>
          AI Assistant
        </div>
      </header>

      <main className="scheme-results-container">
        <div className="scheme-results-heading">
          <p className="conversation-step">STEP 3 OF 4</p>

          <h1>Here are the schemes for you</h1>

          <p>
            Based on the information you provided, these government schemes
            may be relevant to your situation.
          </p>
        </div>

        {results.length === 0 ? (
          <div className="scheme-card">
            <h2>No schemes found</h2>
            <p>
              We could not find a matching government scheme based on the
              information provided.
            </p>
          </div>
        ) : (
          <div className="scheme-list">
            {results.map((scheme) => (
              <div
                className="scheme-card"
                key={scheme.scheme_id}
              >
                <div className="scheme-card-top">
                  <div>
                    <p className="scheme-label">
                      GOVERNMENT SCHEME
                    </p>

                    <h2>{scheme.scheme_name}</h2>
                  </div>

                  <div
                    className={`eligibility-badge ${
                      scheme.eligible
                        ? "eligible"
                        : "not-eligible"
                    }`}
                  >
                    {scheme.eligible
                      ? "✓ Eligible"
                      : "Not eligible"}
                  </div>
                </div>

                <div className="match-score">
                  <strong>{scheme.match_score}%</strong>
                  <span>Match</span>
                </div>

                {scheme.reasons?.length > 0 && (
                  <div className="scheme-section">
                    <h3>Why you match</h3>

                    <ul>
                      {scheme.reasons.map((reason, index) => (
                        <li key={index}>
                          ✓ {reason}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {scheme.failed_conditions?.length > 0 && (
                  <div className="scheme-section">
                    <h3>Requirements not met</h3>

                    <ul>
                      {scheme.failed_conditions.map(
                        (condition, index) => (
                          <li key={index}>
                            ✕ {condition}
                          </li>
                        )
                      )}
                    </ul>
                  </div>
                )}

                {scheme.required_documents?.length > 0 && (
                  <div className="scheme-section">
                    <h3>Documents required</h3>

                    <ul>
                      {scheme.required_documents.map(
                        (document, index) => (
                          <li key={index}>
                            📄 {document}
                          </li>
                        )
                      )}
                    </ul>
                  </div>
                )}

                {scheme.missing_documents?.length > 0 && (
                  <div className="scheme-section">
                    <h3>Missing documents</h3>

                    <ul>
                      {scheme.missing_documents.map(
                        (document, index) => (
                          <li key={index}>
                            ⚠ {document}
                          </li>
                        )
                      )}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        <button
          className="voice-button"
          onClick={() => {
            alert("Document assistance will be connected next.");
          }}
        >
          Continue to documents →
        </button>
      </main>
    </div>
  );
}

export default SchemeResults;