package com.example.demoXM.entity;

import java.util.Date;

public class Hoken {
	//保险id
	private String HKID;
	//保险名
	private String HKN;
	//保险种类
	private String HKSR;
	//保险共通区分
	private String HKKTKB;
	//排他グラフ
	private String HBFLG;
	//简易契约グラフ
	private String KTKYFLG;
	//性别
	private String SEX;
	//贩卖区分
	private String HBKB;
	//ステータス
	private String STS;
	//支付方式
	private String TSKFLGZF;
	//契約方式
	private String TSKFLGQY;
	//料金额
	private String RHN;
	//年龄s
	private Integer NRS;
	//年龄E
	private Integer NRE;
	//登录日期
	private Date INSERTDTE;
	//登录ユーザーid
	private String INSERTID;
	//更新日期
	private Date UPDATEDTE;
	//更新ユーザーid
	private String UPDATEID;


	@Override
	public String toString() {
		return "Hoken [HKID=" + HKID + ", HKN=" + HKN + ", HKSR=" + HKSR + ", HKKTKB=" + HKKTKB + ", HBFLG=" + HBFLG
				+ ", KTKYFLG=" + KTKYFLG + ", SEX=" + SEX + ", HBKB=" + HBKB + ", STS=" + STS + ", TSKFLGZF=" + TSKFLGZF
				+ ", TSKFLGQY=" + TSKFLGQY + ", RHN=" + RHN + ", NRS=" + NRS + ", NRE=" + NRE + ", INSERTDTE="
				+ INSERTDTE + ", INSERTID=" + INSERTID + ", UPDATEDTE=" + UPDATEDTE + ", UPDATEID=" + UPDATEID
				+ ", getTSKFLGZF()=" + getTSKFLGZF() + ", getTSKFLGQY()=" + getTSKFLGQY() + ", getRHN()=" + getRHN()
				+ ", getNRS()=" + getNRS() + ", getNRE()=" + getNRE() + ", getINSERTDTE()=" + getINSERTDTE()
				+ ", getINSERTID()=" + getINSERTID() + ", getUPDATEDTE()=" + getUPDATEDTE() + ", getUPDATEID()="
				+ getUPDATEID() + ", getHBKB()=" + getHBKB() + ", getSTS()=" + getSTS() + ", getSEX()=" + getSEX()
				+ ", getHKID()=" + getHKID() + ", getHKN()=" + getHKN() + ", getHKSR()=" + getHKSR() + ", getHKKTKB()="
				+ getHKKTKB() + ", getHBFLG()=" + getHBFLG() + ", getKTKYFLG()=" + getKTKYFLG() + ", getClass()="
				+ getClass() + ", hashCode()=" + hashCode() + ", toString()=" + super.toString() + "]";
	}
	public String getTSKFLGZF() {
		return TSKFLGZF;
	}
	public void setTSKFLGZF(String tSKFLGZF) {
		TSKFLGZF = tSKFLGZF;
	}
	public String getTSKFLGQY() {
		return TSKFLGQY;
	}
	public void setTSKFLGQY(String tSKFLGQY) {
		TSKFLGQY = tSKFLGQY;
	}
	public String getRHN() {
		return RHN;
	}
	public void setRHN(String rHN) {
		RHN = rHN;
	}
	public Integer getNRS() {
		return NRS;
	}
	public void setNRS(Integer nRS) {
		NRS = nRS;
	}
	public Integer getNRE() {
		return NRE;
	}
	public void setNRE(Integer nRE) {
		NRE = nRE;
	}
	public Date getINSERTDTE() {
		return INSERTDTE;
	}
	public void setINSERTDTE(Date iNSERTDTE) {
		INSERTDTE = iNSERTDTE;
	}
	public String getINSERTID() {
		return INSERTID;
	}
	public void setINSERTID(String iNSERTID) {
		INSERTID = iNSERTID;
	}
	public Date getUPDATEDTE() {
		return UPDATEDTE;
	}
	public void setUPDATEDTE(Date uPDATEDTE) {
		UPDATEDTE = uPDATEDTE;
	}
	public String getUPDATEID() {
		return UPDATEID;
	}
	public void setUPDATEID(String uPDATEID) {
		UPDATEID = uPDATEID;
	}
	public String getHBKB() {
		return HBKB;
	}
	public void setHBKB(String hBKB) {
		HBKB = hBKB;
	}
	public String getSTS() {
		return STS;
	}
	public void setSTS(String sTS) {
		STS = sTS;
	}
	public String getSEX() {
		return SEX;
	}
	public void setSEX(String sEX) {
		SEX = sEX;
	}
	public String getHKID() {
		return HKID;
	}
	public void setHKID(String hKID) {
		HKID = hKID;
	}
	public String getHKN() {
		return HKN;
	}
	public void setHKN(String hKN) {
		HKN = hKN;
	}
	public String getHKSR() {
		return HKSR;
	}
	public void setHKSR(String hKSR) {
		HKSR = hKSR;
	}
	public String getHKKTKB() {
		return HKKTKB;
	}
	public void setHKKTKB(String hKKTKB) {
		HKKTKB = hKKTKB;
	}
	public String getHBFLG() {
		return HBFLG;
	}
	public void setHBFLG(String hBFLG) {
		HBFLG = hBFLG;
	}
	public String getKTKYFLG() {
		return KTKYFLG;
	}
	public void setKTKYFLG(String kTKYFLG) {
		KTKYFLG = kTKYFLG;
	}




}
