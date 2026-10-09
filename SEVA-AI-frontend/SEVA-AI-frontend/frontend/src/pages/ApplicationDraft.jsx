import TranslateTree, { translateText } from "../i18n";

export default function ApplicationDraft({
  selectedScheme,
  profile,
  providedInformation,
  verificationResults,
  language,
  onBack,
}) {
  return (
    <TranslateTree language={language}>
    <div className="page-shell document-page">
      <div className="document-header">
        <div>
          <p className="eyebrow">APPLICATION DRAFT</p>

          <h1>Review your application</h1>

          <p className="page-description">
            Check the information before preparing your final application.
          </p>
        </div>

        {onBack && (
          <button
            className="secondary-button"
            onClick={onBack}
          >
            ← Back to documents
          </button>
        )}
      </div>

      <div className="selected-scheme-banner">
        <div>
          <span className="banner-label">
            Selected scheme
          </span>

          <h2>
            {translateText(language === "kannada" ? (selectedScheme?.scheme_name_kannada || selectedScheme?.scheme_name || "Government Scheme") : (selectedScheme?.scheme_name || "Government Scheme"), language)}
          </h2>
        </div>
      </div>

      <div className="document-card">
        <h3>Applicant information</h3>

        <div className="ocr-data">
          <div>
            <span>Name</span>
            <strong>{profile?.name || "Not provided"}</strong>
          </div>

          <div>
            <span>Gender</span>
            <strong>{profile?.gender || "Not provided"}</strong>
          </div>

          <div>
            <span>Age</span>
            <strong>{profile?.age ?? "Not provided"}</strong>
          </div>

          <div>
            <span>Occupation</span>
            <strong>
              {profile?.occupation || "Not provided"}
            </strong>
          </div>

          <div>
            <span>Annual Income</span>
            <strong>
              {profile?.income !== null &&
              profile?.income !== undefined
                ? `₹${Number(profile.income).toLocaleString(
                    "en-IN"
                  )}`
                : "Not provided"}
            </strong>
          </div>

          <div>
            <span>State</span>
            <strong>{profile?.state || "Not provided"}</strong>
          </div>

          <div>
            <span>District</span>
            <strong>
              {profile?.district || "Not provided"}
            </strong>
          </div>

          <div>
            <span>Category</span>
            <strong>
              {profile?.category || "Not provided"}
            </strong>
          </div>

          <div>
            <span>Problem</span>
            <strong>
              {profile?.problem || "Not provided"}
            </strong>
          </div>
        </div>
      </div>

      {providedInformation &&
        Object.keys(providedInformation).length > 0 && (
          <div className="document-card">
            <h3>Additional information</h3>

            <div className="ocr-data">
              {Object.entries(providedInformation).map(
                ([key, value]) => (
                  <div key={key}>
                    <span>{key}</span>

                    <strong>
                      {value || "Not provided"}
                    </strong>
                  </div>
                )
              )}
            </div>
          </div>
        )}

      <div className="document-card">
        <h3>Document verification</h3>

        {Object.keys(verificationResults || {}).length === 0 ? (
          <p>
            No uploaded documents were submitted for
            verification.
          </p>
        ) : (
          Object.entries(verificationResults).map(
            ([index, result]) => {
              const verification = result?.verification;

              return (
                <div
                  className={
                    verification?.verified
                      ? "verification-result verification-success"
                      : "verification-result verification-failed"
                  }
                  key={index}
                >
                  <div className="verification-icon">
                    {verification?.verified ? "✓" : "!"}
                  </div>

                  <div className="verification-content">
                    <h4>
                      {verification?.verified
                        ? "Document verified"
                        : "Document needs attention"}
                    </h4>

                    <p>
                      {verification?.verified
                        ? "The uploaded document matches the available profile information."
                        : "The uploaded document was not fully verified."}
                    </p>
                  </div>
                </div>
              );
            }
          )
        )}
      </div>

      <div className="documents-footer">
        <button
          className="primary-button"
          onClick={() => window.print()}
        >
          Print / Save Application Draft
        </button>
      </div>
    </div>
    </TranslateTree>
  );
}
