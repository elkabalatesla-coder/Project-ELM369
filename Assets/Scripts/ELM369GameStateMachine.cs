using System;
using UnityEngine;

public class ELM369GameStateMachine : MonoBehaviour
{
    public const string ProjectIdentifier = "JMR0824197846902";
    public const string CompanionIdentifier = "JMR08241978202646902";

    public enum GamePhase
    {
        Lobby,
        Init,
        PlayerTurn,
        AITurn,
        Resolution,
        GameOver
    }

    public GamePhase CurrentPhase { get; private set; } = GamePhase.Lobby;

    public event Action<GamePhase> OnPhaseChanged;

    public void ChangePhase(GamePhase newPhase)
    {
        if (!Enum.IsDefined(typeof(GamePhase), newPhase))
        {
            throw new ArgumentOutOfRangeException(nameof(newPhase));
        }

        if (CurrentPhase == newPhase)
        {
            return;
        }

        CurrentPhase = newPhase;
        OnPhaseChanged?.Invoke(newPhase);
    }
}
