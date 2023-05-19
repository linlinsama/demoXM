package com.example.demoXM.entity;

public class User {
	//社员区分 0是会员 1是社员
	private String SYIKUBUN;
	//登录别名
	private String lOGINN;
	//密码
	private String PASS;
	public String getSYIKUBUN() {
		return SYIKUBUN;
	}
	public void setSYIKUBUN(String sYIKUBUN) {
		SYIKUBUN = sYIKUBUN;
	}
	public String getlOGINN() {
		return lOGINN;
	}
	public void setlOGINN(String lOGINN) {
		this.lOGINN = lOGINN;
	}
	public String getPASS() {
		return PASS;
	}
	public void setPASS(String pASS) {
		PASS = pASS;
	}




}
