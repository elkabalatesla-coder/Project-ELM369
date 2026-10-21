using UnityEngine;

[RequireComponent(typeof(AudioSource), typeof(AudioReverbFilter))]
public class ELM369BinauralAcousticEngine : MonoBehaviour
{
    public const string ProjectIdentifier = "JMR08241978202646902";

    [Header("Acoustic Raytracing Settings")]
    public LayerMask roomGeometryLayer;
    [Min(1)] public int raycastSampleCount = 32;
    [Min(0.01f)] public float maxAudioDistance = 25.0f;

    [Header("Material Absorption Coefficients")]
    [Range(0.0f, 1.0f)] public float woodAbsorption = 0.15f;
    [Range(0.0f, 1.0f)] public float feltClothAbsorption = 0.65f;
    [Range(0.0f, 1.0f)] public float glassStoneAbsorption = 0.05f;

    private AudioReverbFilter reverbFilter;

    private void Start()
    {
        ComputeRoomAcoustics();
    }

    public void ComputeRoomAcoustics()
    {
        if (reverbFilter == null)
        {
            reverbFilter = GetComponent<AudioReverbFilter>();
        }

        if (reverbFilter == null)
        {
            return;
        }

        float totalHitDistance = 0.0f;
        float cumulativeMaterialAbsorption = 0.0f;
        int validHits = 0;
        int sampleCount = Mathf.Max(1, raycastSampleCount);
        float rayDistance = Mathf.Max(0.01f, maxAudioDistance);

        for (int i = 0; i < sampleCount; i++)
        {
            RaycastHit hit;
            if (!Physics.Raycast(transform.position, Random.onUnitSphere, out hit,
                rayDistance, roomGeometryLayer, QueryTriggerInteraction.Ignore))
            {
                continue;
            }

            totalHitDistance += hit.distance;
            validHits++;

            // Reading the assigned tag also works when optional material tags are not defined.
            string surfaceTag = hit.collider.tag;
            if (surfaceTag == "Wood")
            {
                cumulativeMaterialAbsorption += Mathf.Clamp01(woodAbsorption);
            }
            else if (surfaceTag == "Felt" || surfaceTag == "Cloth")
            {
                cumulativeMaterialAbsorption += Mathf.Clamp01(feltClothAbsorption);
            }
            else
            {
                cumulativeMaterialAbsorption += Mathf.Clamp01(glassStoneAbsorption);
            }
        }

        // Clear a previous room's reverb when no enclosing geometry is detected.
        reverbFilter.enabled = validHits > 0;
        if (validHits > 0)
        {
            UpdateRoomAcoustics(totalHitDistance / validHits,
                cumulativeMaterialAbsorption / validHits);
        }
    }

    private void UpdateRoomAcoustics(float avgDistance, float avgAbsorption)
    {
        float roomScale = Mathf.Clamp(avgDistance / 12.0f, 0.1f, 1.0f);
        reverbFilter.reverbPreset = AudioReverbPreset.User;
        // AudioReverbFilter has no roomSize property; room is a level in millibels.
        reverbFilter.room = Mathf.Lerp(-1000.0f, 0.0f, roomScale);
        reverbFilter.decayTime = Mathf.Clamp(
            (avgDistance * 0.15f) * (1.0f - avgAbsorption * 0.5f), 0.3f, 6.0f);
        reverbFilter.hfReference = 5000.0f;
        reverbFilter.roomHF = Mathf.Lerp(-1000.0f, -10000.0f, avgAbsorption);

        Debug.Log($"[ELM369 - {ProjectIdentifier}] Advanced Acoustic Raytrace Complete. " +
                  $"Room Scale: {roomScale:F2}, Decay Time: {reverbFilter.decayTime:F2}s, " +
                  $"Avg Absorption: {avgAbsorption:F2}.");
    }
}
