uniform float czas;
uniform vec3 pozycja_ogniskowa;

void main() {
    vec2 uv = gl_FragCoord.xy/iResolution.xy;
    vec3 kolor = vec3(0.0);
    
    // Dynamiczny efekt tunelu kwantowego
    float animacja = sin(czas * 0.5) * 0.5 + 0.5;
    vec2 p = uv * 2.0 - 1.0;
    float promień = length(p) * (1.0 + animacja);
    float kat = atan(p.y, p.x) + czas * 2.0;
    
    // Efekt spiralnego strumienia
    kolor.r = sin(promięć * 20.0 + kat * 5.0 + czas);
    kolor.g = cos(promieć * 15.0 - kat * 3.0 + czas);
    kolor.b = sin(promieć * 10.0 + kat * 7.0 - czas);
    
    gl_FragColor = vec4(kolor * 2.0, 1.0);
}
uniform sampler2D szum_kwantowy;

void main() {
    vec2 uv = gl_FragCoord.xy/iResolution.xy * 2.0 - 1.0;
    vec3 kolor = vec3(0.0);
    
    // Dynamiczna interferencja kwantowa
    float faza = czas * 2.0 + length(uv) * 10.0;
    vec3 szum = texture(szum_kwantowy, uv * 0.5 + czas * 0.1).rgb;
    
    // Efekt splątania kwantowego
    kolor.r = sin(faza * 3.0 + szum.r * 10.0);
    kolor.g = cos(faza * 2.0 + szum.g * 8.0);
    kolor.b = sin(faza * 4.0 + szum.b * 6.0);
    
    // Głębia przestrzenna
    float mgła = exp(-length(uv) * 2.0);
    gl_FragColor = vec4(kolor * mgła * 2.0, 1.0);
}