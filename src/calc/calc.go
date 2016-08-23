package calc

/**/
func Slg (single, double, triple, HR, AB int) float64 {
	return float64(single + (double * 2) + (triple * 3) + (HR * 4)) / float64(AB)
}


/**/
func OBP (hits, bb, hbp, ab, sac int) float64 {
	var num   = hits + bb + hbp
	var denom = ab + bb + hbp + sac
	return float64(num) / float64(denom)
}


/**/
func OPS (slg, obp float64) float64 {
	return slg + obp
}


/**/
func BABIP (hits, hr, ab, k, sf int) float64 {
	return float64(hits - hr) / float64(ab - k - hr + sf)
}
