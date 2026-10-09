import { useEffect, useState } from "react";
import { searchWebSchemes } from "../services/api";
import TranslateTree, { translateText } from "../i18n";

function SchemeResults({
  eligibilityResults,
  onContinueDocuments,
  language,
}) {
  const [webResults, setWebResults] = useState([]);
  const [sources, setSources] = useState([]);
  const [isSearching, setIsSearching] = useState(true);
  const [error, setError] = useState("");
  const [selectedScheme, setSelectedScheme] =
    useState(null);

  const profile = eligibilityResults?.citizen;

  useEffect(() => {
    let cancelled = false;

    async function loadSchemes() {
      if (!profile) {
        setError("Citizen information is missing.");
        setIsSearching(false);
        return;
      }

      try {
        setIsSearching(true);
        setError("");

        const data = await searchWebSchemes(profile, language);

        if (cancelled) {
          return;
        }

        setWebResults(data.results || []);
        setSources(data.sources || []);
      } catch (error) {
        console.error("Scheme search error:", error);

        if (!cancelled) {
          setError(
            "Live government scheme search failed. Showing the available eligibility results instead."
          );
        }
      } finally {
        if (!cancelled) {
          setIsSearching(false);
        }
      }
    }

    loadSchemes();

    return () => {
      cancelled = true;
    };
  }, [profile, language]);

  const fallbackResults =
    eligibilityResults?.results || [];

  const results =
    webResults.length > 0
      ? webResults
      : fallbackResults.map((scheme) => ({
          scheme_name: scheme.scheme_name,
          benefits: [],
          eligibility_requirements: [],
          required_documents:
            scheme.required_documents || [],
          eligibility_status: scheme.eligible
            ? "eligible"
            : "not_eligible",
          matched_conditions:
            scheme.reasons || [],
          failed_conditions:
            scheme.failed_conditions || [],
          verification_notes:
            scheme.missing_documents || [],
          source_url: "",
          source_title: "",
        }));

  const handleSelectScheme = (scheme) => {
    setSelectedScheme(scheme);
  };

  const handleContinue = () => {
    if (!selectedScheme) {
      return;
    }

    onContinueDocuments(selectedScheme);
  };

  return (
    <TranslateTree language={language}>
    <div className="scheme-results-screen">
      <header className="conversation-top">
        <div className="brand">
          <div className="brand-icon">S</div>

          <div className="brand-text">
            <span>SEVA AI</span>
            <small>Citizen Assistance</small>
          </div>
        </div>

        <div className="conversation-status">
          <span className="status-dot"></span>
          Live Government Search
        </div>
      </header>

      <main className="scheme-results-container">
        <div className="scheme-results-heading">
          <p className="conversation-step">
            STEP 3 OF 4
          </p>

          <h1>
            Schemes that may help you
          </h1>

          <p>
            We found government services and schemes
            related to your situation. Review the
            requirements and select the one you want
            to proceed with.
          </p>
        </div>

        {isSearching && (
          <div className="scheme-card">
            <h2>
              Searching government sources...
            </h2>

            <p>
              SEVA AI is checking current government
              information, requirements and eligibility.
            </p>

            <div className="scheme-search-loading">
              <div className="loading-dot"></div>
              <div className="loading-dot"></div>
              <div className="loading-dot"></div>
            </div>
          </div>
        )}

        {!isSearching && error && (
          <div className="scheme-card">
            <h2>
              Live search unavailable
            </h2>

            <p>{error}</p>
          </div>
        )}

        {!isSearching &&
          results.length === 0 && (
            <div className="scheme-card">
              <h2>
                No schemes found
              </h2>

              <p>
                We could not find a relevant government
                scheme from the available information.
              </p>
            </div>
          )}

        {!isSearching &&
          results.length > 0 && (
            <>
              <div className="scheme-list">
                {results.map((scheme, index) => {
                  const status =
                    scheme.eligibility_status ||
                    "needs_verification";

                  const isSelected =
                    selectedScheme?.scheme_name ===
                      scheme.scheme_name &&
                    selectedScheme?.source_url ===
                      scheme.source_url;

                  const canSelect =
                    status !== "not_eligible";

                  return (
                    <div
                      className={`scheme-card ${
                        isSelected
                          ? "scheme-card-selected"
                          : ""
                      }`}
                      key={
                        scheme.source_url ||
                        `${scheme.scheme_name}-${index}`
                      }
                    >
                      <div className="scheme-card-top">
                        <div>
                          <p className="scheme-label">
                            GOVERNMENT SCHEME / SERVICE
                          </p>

                          <h2>
                            {translateText(language === "kannada" ? (scheme.scheme_name_kannada || scheme.scheme_name) : scheme.scheme_name, language)}
                          </h2>
                        </div>

                        <div
                          className={`eligibility-badge ${status}`}
                        >
                          {status === "eligible" &&
                            "✓ Likely eligible"}

                          {status === "not_eligible" &&
                            "✕ Not eligible"}

                          {status ===
                            "needs_verification" &&
                            "⚠ Needs verification"}
                        </div>
                      </div>

                      {scheme.benefits?.length > 0 && (
                        <div className="scheme-section">
                          <h3>
                            What this scheme provides
                          </h3>

                          <ul>
                            {scheme.benefits.map(
                              (
                                benefit,
                                itemIndex
                              ) => (
                                <li key={itemIndex}>
                                  ✓ {benefit}
                                </li>
                              )
                            )}
                          </ul>
                        </div>
                      )}

                      {scheme.eligibility_requirements
                        ?.length > 0 && (
                        <div className="scheme-section">
                          <h3>
                            Eligibility requirements
                          </h3>

                          <ul>
                            {scheme.eligibility_requirements.map(
                              (
                                requirement,
                                itemIndex
                              ) => (
                                <li key={itemIndex}>
                                  • {requirement}
                                </li>
                              )
                            )}
                          </ul>
                        </div>
                      )}

                      {scheme.matched_conditions
                        ?.length > 0 && (
                        <div className="scheme-section">
                          <h3>
                            Why you match
                          </h3>

                          <ul>
                            {scheme.matched_conditions.map(
                              (
                                condition,
                                itemIndex
                              ) => (
                                <li key={itemIndex}>
                                  ✓ {condition}
                                </li>
                              )
                            )}
                          </ul>
                        </div>
                      )}

                      {scheme.failed_conditions
                        ?.length > 0 && (
                        <div className="scheme-section">
                          <h3>
                            Requirements not met
                          </h3>

                          <ul>
                            {scheme.failed_conditions.map(
                              (
                                condition,
                                itemIndex
                              ) => (
                                <li key={itemIndex}>
                                  ✕ {condition}
                                </li>
                              )
                            )}
                          </ul>
                        </div>
                      )}

                      {scheme.required_documents
                        ?.length > 0 && (
                        <div className="scheme-section">
                          <h3>
                            Documents required
                          </h3>

                          <ul>
                            {scheme.required_documents.map(
                              (
                                document,
                                itemIndex
                              ) => (
                                <li key={itemIndex}>
                                  📄 {document}
                                </li>
                              )
                            )}
                          </ul>
                        </div>
                      )}

                      {scheme.verification_notes
                        ?.length > 0 && (
                        <div className="scheme-section">
                          <h3>
                            What still needs verification
                          </h3>

                          <ul>
                            {scheme.verification_notes.map(
                              (
                                note,
                                itemIndex
                              ) => (
                                <li key={itemIndex}>
                                  ⚠ {note}
                                </li>
                              )
                            )}
                          </ul>
                        </div>
                      )}

                      {scheme.source_url && (
                        <div className="scheme-source">
                          <span>
                            Official source:
                          </span>

                          <a
                            href={
                              scheme.source_url
                            }
                            target="_blank"
                            rel="noreferrer"
                          >
                            {scheme.source_title ||
                              "Government source"}
                          </a>
                        </div>
                      )}

                      <div className="scheme-card-action">
                        <button
                          className={
                            isSelected
                              ? "scheme-select-button selected"
                              : "scheme-select-button"
                          }
                          disabled={!canSelect}
                          onClick={() =>
                            handleSelectScheme(
                              scheme
                            )
                          }
                        >
                          {isSelected
                            ? "✓ Scheme selected"
                            : "Select this scheme"}

                          {!isSelected && (
                            <span>→</span>
                          )}
                        </button>
                      </div>

                      <div className="scheme-verification-warning">
                        <strong>
                          AI assessment
                        </strong>

                        <p>
                          This assessment is based on
                          information retrieved from
                          government sources. Final
                          eligibility is determined by
                          the relevant government
                          department.
                        </p>
                      </div>
                    </div>
                  );
                })}
              </div>

              {selectedScheme && (
                <div className="selected-scheme-bar">
                  <div>
                    <span>
                      SELECTED SCHEME
                    </span>

                    <strong>
                      {translateText(language === "kannada" ? (selectedScheme.scheme_name_kannada || selectedScheme.scheme_name) : selectedScheme.scheme_name, language)}
                    </strong>
                  </div>

                  <button
                    className="voice-button"
                    onClick={handleContinue}
                  >
                    Continue to documents →
                  </button>
                </div>
              )}

              {sources.length > 0 && (
                <div className="scheme-sources">
                  <h2>
                    Sources checked
                  </h2>

                  <div>
                    {sources.map(
                      (source, index) => (
                        <a
                          key={index}
                          href={source.url}
                          target="_blank"
                          rel="noreferrer"
                        >
                          {source.title ||
                            source.url}
                        </a>
                      )
                    )}
                  </div>
                </div>
              )}
            </>
          )}
      </main>
    </div>
    </TranslateTree>
  );
}

export default SchemeResults;
