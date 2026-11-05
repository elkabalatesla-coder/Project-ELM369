using UnityEngine;
using UnityEngine.UI;

public class ELM369GameHUD : MonoBehaviour
{
    public const string ProjectIdentifier = "JMR0824197846902";
    public const string CompanionIdentifier = "JMR08241978202646902";

    [Header("UI Bindings")]
    public ELM369GameStateMachine gameStateMachine;
    public Text phaseStatusText;
    public Image hudAccentPanel;

    [Header("Theme Colors")]
    public Color playerTurnColor = new Color(0.1f, 0.6f, 1.0f);
    public Color aiTurnColor = new Color(0.9f, 0.2f, 0.2f);
    public Color resolutionColor = new Color(1.0f, 0.8f, 0.1f);

    private ELM369GameStateMachine subscribedStateMachine;

    private void OnEnable()
    {
        subscribedStateMachine = gameStateMachine;
        if (subscribedStateMachine != null)
        {
            subscribedStateMachine.OnPhaseChanged += HandlePhaseChanged;
            HandlePhaseChanged(subscribedStateMachine.CurrentPhase);
        }
    }

    private void OnDisable()
    {
        if (subscribedStateMachine != null)
        {
            subscribedStateMachine.OnPhaseChanged -= HandlePhaseChanged;
        }

        subscribedStateMachine = null;
    }

    private void HandlePhaseChanged(ELM369GameStateMachine.GamePhase newPhase)
    {
        if (phaseStatusText != null)
        {
            phaseStatusText.text = $"ELM369 Phase: {newPhase.ToString().ToUpperInvariant()}";
        }

        if (hudAccentPanel != null)
        {
            switch (newPhase)
            {
                case ELM369GameStateMachine.GamePhase.PlayerTurn:
                    hudAccentPanel.color = playerTurnColor;
                    break;
                case ELM369GameStateMachine.GamePhase.AITurn:
                    hudAccentPanel.color = aiTurnColor;
                    break;
                case ELM369GameStateMachine.GamePhase.Resolution:
                case ELM369GameStateMachine.GamePhase.GameOver:
                    hudAccentPanel.color = resolutionColor;
                    break;
                default:
                    hudAccentPanel.color = Color.gray;
                    break;
            }
        }

        Debug.Log($"[ELM369 HUD - {ProjectIdentifier}] UI Updated for Phase: {newPhase}");
    }
}
